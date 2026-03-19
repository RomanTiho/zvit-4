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
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings


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
        """
        Тимчасово вимкнено небезпечний скидання пароля за username.
        Замість цього використовуйте request_password_reset / confirm_password_reset.
        """
        return Response(
            {'error': 'Скидання пароля через логін вимкнено з міркувань безпеки.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def request_password_reset(self, request):
        """
        Запит скидання пароля по email.
        Надсилає лист з посиланням, яке містить uid та токен.
        """
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Вкажіть email'}, status=status.HTTP_400_BAD_REQUEST)

        # Шукаємо користувача за email
        user = User.objects.filter(email__iexact=email).order_by('id').first()
        if not user:
            # Змінено: Повертаємо 400 помилку з чітким повідомленням
            return Response(
                {'error': 'Користувача з таким email не знайдено.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_generator = PasswordResetTokenGenerator()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_url = f"{getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:8000')}/reset-password.html?uid={uidb64}&token={token}"

        subject = 'Скидання пароля FootballHub'
        message = (
            "Ви отримали цей лист, тому що запросили скидання пароля на FootballHub.\n\n"
            f"Щоб встановити новий пароль, перейдіть за посиланням:\n{reset_url}\n\n"
            "Якщо ви не робили цей запит, просто ігноруйте лист."
        )

        try:
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                [user.email],
                fail_silently=False,
            )
        except Exception:
            # Приховуємо оригінальну помилку для користувача, але кажемо що щось пішло не так
            return Response({'error': 'Не вдалося надіслати лист. Перевірте налаштування поштового сервера або спробуйте пізніше.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {'message': 'Лист успішно відправлено на вашу пошту!'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def confirm_password_reset(self, request):
        """
        Підтвердження скидання пароля за uid + токен з листа.
        Очікує: uid, token, new_password, confirm_password.
        """
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not uidb64 or not token:
            return Response({'error': 'Невірне посилання для скидання пароля'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password:
            return Response({'error': 'Вкажіть новий пароль'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Паролі не співпадають'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': 'Пароль має містити щонайменше 8 символів'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({'error': 'Невірне посилання для скидання пароля'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({'error': 'Посилання для скидання пароля недійсне або прострочене'}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def coach_stats(self, request):
        """Статистика тренера — команди, турніри, матчі, перемоги"""
        user = request.user
        # Команди цього тренера
        teams = Team.objects.filter(coach=user)
        team_count = teams.count()
        # Унікальні турніри, в яких беруть участь команди тренера
        tournament_ids = teams.values_list('tournament_id', flat=True).distinct()
        tournament_count = len(set(tournament_ids))
        # Матчі в цих турнірах
        team_names = list(teams.values_list('name', flat=True))
        from django.db.models import Q
        matches_qs = Match.objects.filter(tournament_id__in=tournament_ids)
        match_count = matches_qs.count()
        # Перемоги (матчі де команда тренера перемогла)
        wins = 0
        for m in matches_qs:
            if m.home_team in team_names and m.home_score > m.away_score:
                wins += 1
            elif m.away_team in team_names and m.away_score > m.home_score:
                wins += 1
        # Останні турніри
        from .serializers import TournamentSerializer as TS
        recent_tournaments = Tournament.objects.filter(id__in=tournament_ids).order_by('-start_date')[:5]
        recent_data = [{'id': t.id, 'name': t.name, 'status': t.status, 'format': t.format, 'start_date': str(t.start_date)} for t in recent_tournaments]
        return Response({
            'teams': team_count,
            'tournaments': tournament_count,
            'matches': match_count,
            'wins': wins,
            'recent_tournaments': recent_data,
        })


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
