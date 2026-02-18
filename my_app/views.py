from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Player, PlayerStats
from .serializers import (
    PlayerSerializer, 
    PlayerDetailSerializer,
    PlayerStatsSerializer,
    PlayerRatingHistorySerializer,
    UserRegisterSerializer,
    UserProfileSerializer,
    UserUpdateSerializer
)
from .services import PlayerRatingService


class AuthViewSet(viewsets.ViewSet):
    """ViewSet для авторизації та реєстрації"""
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Реєстрація нового користувача"""
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Створити JWT токени
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Отримати поточного користувача"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Оновити профіль користувача"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Вихід з системи (blacklist refresh token)"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для публічних профілів"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Отримати статистику гравця"""
        user = self.get_object()
        
        try:
            player = user.player
            stats = PlayerRatingService.get_player_statistics(player)
            
            return Response({
                'player_id': player.id,
                'position': player.position,
                'overall_rating': float(player.overall_rating),
                'matches_played': player.matches_played,
                'statistics': stats
            })
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PlayerViewSet(viewsets.ModelViewSet):
    """ViewSet для управління гравцями"""
    queryset = Player.objects.select_related('user').prefetch_related('stats', 'rating_history')
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlayerDetailSerializer
        return PlayerSerializer
    
    @action(detail=True, methods=['get'])
    def rating_history(self, request, pk=None):
        """Отримати історію рейтингу гравця"""
        player = self.get_object()
        history = player.rating_history.all()[:20]
        serializer = PlayerRatingHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_stats(self, request, pk=None):
        """Оновити статистику після матчу"""
        player = self.get_object()
        serializer = PlayerStatsSerializer(data=request.data)
        
        if serializer.is_valid():
            stats = serializer.save(player=player)
            # Перерахувати рейтинг
            new_rating = PlayerRatingService.calculate_rating(player)
            
            return Response({
                'message': 'Stats updated successfully',
                'new_rating': float(new_rating),
                'stats': PlayerStatsSerializer(stats).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Топ гравців за рейтингом"""
        position = request.query_params.get('position')
        limit = int(request.query_params.get('limit', 50))
        
        queryset = self.queryset
        
        if position:
            queryset = queryset.filter(position=position)
        
        top_players = queryset.order_by('-overall_rating')[:limit]
        serializer = self.get_serializer(top_players, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Пошук гравців"""
        query = request.query_params.get('q', '')
        position = request.query_params.get('position')
        min_rating = request.query_params.get('min_rating')
        
        queryset = self.queryset
        
        if query:
            queryset = queryset.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            )
        
        if position:
            queryset = queryset.filter(position=position)
        
        if min_rating:
            queryset = queryset.filter(overall_rating__gte=float(min_rating))
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PlayerStatsViewSet(viewsets.ModelViewSet):
    """ViewSet для статистики гравців"""
    queryset = PlayerStats.objects.select_related('player__user')
    serializer_class = PlayerStatsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        player_id = self.request.query_params.get('player_id')
        match_id = self.request.query_params.get('match_id')
        
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        
        return queryset
