from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import include, path, reverse

import pytest
from rest_framework.test import APIClient

from .models import Player, PlayerRatingHistory, PlayerStats
from .urls import router

urlpatterns = [
    path("", include(router.urls)),
]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def player_user():
    user = User.objects.create_user(username="testplayer", password="pwd")
    return Player.objects.create(
        user=user, position="MID", overall_rating=Decimal("7.5")
    )


@pytest.mark.django_db
@pytest.mark.urls(__name__)
class TestPlayerViews:
    def test_list_players(self, api_client, player_user):
        url = reverse("player-list")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_retrieve_player(self, api_client, player_user):
        url = reverse("player-detail", args=[player_user.id])
        response = api_client.get(url)
        assert response.status_code == 200

    def test_rating_history(self, api_client, player_user):
        PlayerRatingHistory.objects.create(player=player_user, rating=Decimal("7.5"))
        url = reverse("player-rating-history", args=[player_user.id])
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_leaderboard(self, api_client, player_user):
        url = reverse("player-leaderboard")
        response = api_client.get(url)
        assert response.status_code == 200

    def test_search(self, api_client, player_user):
        url = reverse("player-search")
        response = api_client.get(url + "?q=testplayer")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_player_stats_list(self, api_client, player_user):
        PlayerStats.objects.create(player=player_user, match_id=1, goals=1)
        url = reverse("playerstats-list")
        response = api_client.get(url + f"?player_id={player_user.id}")
        assert response.status_code == 200

        # Test match_id filter
        response = api_client.get(url + "?match_id=1")
        assert response.status_code == 200

    def test_update_stats(self, api_client, player_user):
        url = reverse("player-update-stats", args=[player_user.id])
        data = {"match_id": 2, "goals": 1, "assists": 1, "minutes_played": 90}
        api_client.force_authenticate(user=player_user.user)
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

        # Test bad request
        bad_data = {"missing": "fields"}
        response = api_client.post(url, bad_data, format="json")
        assert response.status_code == 400
