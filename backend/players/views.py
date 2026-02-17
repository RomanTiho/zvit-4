from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from .models import Player, PlayerStats
from .serializers import (
    PlayerSerializer, 
    PlayerDetailSerializer,
    PlayerStatsSerializer,
    PlayerRatingHistorySerializer
)
from .services import PlayerRatingService


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
    
    @action(detail=True, methods=['post'])
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
