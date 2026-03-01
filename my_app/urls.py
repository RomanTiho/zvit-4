from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    PlayerViewSet, PlayerStatsViewSet, AuthViewSet, ProfileViewSet, 
    upl_squad_view, upl_sync_view,
    TournamentViewSet, TeamViewSet, StandingViewSet, MatchViewSet
)

router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'player-stats', PlayerStatsViewSet, basename='playerstats')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'tournaments', TournamentViewSet, basename='tournament')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'standings', StandingViewSet, basename='standing')
router.register(r'matches', MatchViewSet, basename='match')


urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # UPL squad endpoints
    path('upl/squad/<str:team_name>/', upl_squad_view, name='upl_squad'),
    path('upl/sync/', upl_sync_view, name='upl_sync'),

    # Router URLs
    path('', include(router.urls)),
]
