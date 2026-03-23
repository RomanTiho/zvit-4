from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import PlayerStatsViewSet, PlayerViewSet

router = DefaultRouter()
router.register(r"players", PlayerViewSet, basename="player")
router.register(r"player-stats", PlayerStatsViewSet, basename="playerstats")

urlpatterns = [
    path("", include(router.urls)),
]
