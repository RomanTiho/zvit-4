from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlayerViewSet, PlayerStatsViewSet

router = DefaultRouter()
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'player-stats', PlayerStatsViewSet, basename='playerstats')

urlpatterns = [
    path('', include(router.urls)),
]
