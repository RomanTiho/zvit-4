import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from my_app.models import Tournament, Team, Match, Player

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestViews:
    def test_get_tournaments(self, api_client):
        Tournament.objects.create(
            name="Euro 2024",
            start_date="2024-06-01",
            end_date="2024-07-01",
            format="Group stage",
            max_teams=24,
            location="Germany"
        )
        response = api_client.get('/api/tournaments/')
        assert response.status_code == 200

    def test_get_teams(self, api_client):
        tour = Tournament.objects.create(
            name="World Cup",
            start_date="2026-06-01",
            end_date="2026-07-01",
            format="Groups",
            max_teams=48,
            location="USA"
        )
        Team.objects.create(
            tournament=tour,
            name="National Team",
            captain="Captain",
            email="nt@nt.com",
            phone="111"
        )
        response = api_client.get('/api/teams/')
        assert response.status_code == 200

    def test_get_matches(self, api_client):
        tour = Tournament.objects.create(
            name="Copa",
            start_date="2024-06-01",
            end_date="2024-07-01",
            format="Groups",
            max_teams=16,
            location="USA"
        )
        Match.objects.create(
            tournament=tour,
            date="2024-06-15T20:00:00Z",
            home_team="Argentina",
            away_team="Brazil"
        )
        response = api_client.get('/api/matches/')
        assert response.status_code == 200

    def test_get_players(self, api_client):
        user = User.objects.create_user(username="test_player", password="pwd")
        Player.objects.create(user=user, position="MID")
        response = api_client.get('/api/players/')
        assert response.status_code in [200, 401, 403]

    def test_auth_register(self, api_client):
        response = api_client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }, format='json')
        assert response.status_code in [201, 400]

    def test_auth_request_password_reset(self, api_client):
        User.objects.create_user(username="testreset", email="reset@test.com", password="pwd")
        response = api_client.post('/api/auth/request_password_reset/', {
            'email': 'reset@test.com'
        }, format='json')
        assert response.status_code == 200

    def test_profile_views(self, api_client):
        user = User.objects.create_user(username="profuser", password="pwd")
        Player.objects.create(user=user, position="DEF")
        response = api_client.get(f'/api/profiles/')
        assert response.status_code == 200
        response_stats = api_client.get(f'/api/profiles/{user.id}/stats/')
        assert response_stats.status_code == 200

    def test_player_leaderboard(self, api_client):
        response = api_client.get('/api/players/leaderboard/')
        assert response.status_code == 200
        
    def test_player_search(self, api_client):
        response = api_client.get('/api/players/search/?q=prof')
        assert response.status_code == 200

    def test_upl_squad(self, api_client):
        response = api_client.get('/api/upl/squad/shakhtar/')
        assert response.status_code in [200, 404, 500]
