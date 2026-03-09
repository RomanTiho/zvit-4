from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny, BasePermission
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Player, PlayerStats, UserProfile
from .serializers import (
    PlayerSerializer, 
    PlayerDetailSerializer,
    PlayerStatsSerializer,
    PlayerRatingHistorySerializer,
    UserRegisterSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    TournamentSerializer,
    TeamSerializer,
    StandingSerializer,
    MatchSerializer
)
from .models import Player, PlayerStats, Tournament, Team, Standing, Match, UserProfile
from .services import PlayerRatingService


class IsCoach(BasePermission):
    """Дозвіл тільки для членів групи Coach"""
    message = 'Доступно тільки для тренерів.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Coach').exists()
        )


class IsAdminOrCoach(BasePermission):
    """Дозвіл для адмінів або членів групи Coach"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name='Coach').exists()


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.prefetch_related('teams', 'standings', 'matches')
    serializer_class = TournamentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Створення/редагування/видалення турніру — тільки адмін або тренер
        return [IsAdminOrCoach()]

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOrCoach()]

    def perform_create(self, serializer):
        # Автоматично зберігаємо поточного користувача як тренера команди
        serializer.save(coach=self.request.user)

class StandingViewSet(viewsets.ModelViewSet):
    queryset = Standing.objects.all()
    serializer_class = StandingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]



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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """Скидання пароля за username"""
        username = request.data.get('username', '').strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not username or not new_password:
            return Response({'error': "Вкажіть ім'я користувача та новий пароль"},
                            status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': 'Паролі не співпадають'},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 8:
            return Response({'error': 'Пароль має містити щонайменше 8 символів'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Користувача з таким іменем не знайдено'},
                            status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Пароль успішно змінено'}, status=status.HTTP_200_OK)

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
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated],
            parser_classes=[MultiPartParser, FormParser])
    def upload_avatar(self, request):
        """Завантажити аватар тренера"""
        if 'avatar' not in request.FILES:
            return Response({'error': 'Файл не знайдено. Передайте поле avatar.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['avatar']
        # Перевірка типу файлу
        if not file.content_type.startswith('image/'):
            return Response({'error': 'Дозволені лише зображення.'}, status=status.HTTP_400_BAD_REQUEST)
        # Обмеження розміру — 5 МБ
        if file.size > 5 * 1024 * 1024:
            return Response({'error': 'Розмір файлу не може перевищувати 5 МБ.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Видалити старий аватар якщо є
        if profile.avatar:
            profile.avatar.delete(save=False)

        profile.avatar = file
        profile.save()

        avatar_url = request.build_absolute_uri(profile.avatar.url)
        return Response({'avatar_url': avatar_url}, status=status.HTTP_200_OK)

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


# ===== UPL Squad Views =====
from .upl_service import get_squad, UPL_TEAM_IDS
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])
def upl_squad_view(request, team_name):
    """
    GET /api/upl/squad/<team_name>/
    Returns squad data for the given UPL team name.
    Uses 24-hour SQLite cache to minimise API calls.
    """
    result = get_squad(team_name)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upl_sync_view(request):
    """
    POST /api/upl/sync/
    Force-refresh all UPL team squads from API (admin only).
    """
    if not request.user.is_staff:
        return Response({'detail': 'Тільки адміністратори.'}, status=status.HTTP_403_FORBIDDEN)

    results = {}
    for team_name in UPL_TEAM_IDS:
        from .models import UPLSquadCache
        UPLSquadCache.objects.filter(team_name=team_name).delete()
        data = get_squad(team_name)
        results[team_name] = {'players': len(data.get('players', [])), 'source': data.get('source')}

    return Response({'synced': results})
