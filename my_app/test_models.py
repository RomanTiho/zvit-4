from decimal import Decimal

from django.contrib.auth.models import User

import pytest

from my_app.models import (
    Match,
    Player,
    PlayerRatingHistory,
    PlayerStats,
    Standing,
    Team,
    Tournament,
    UPLSquadCache,
    UserProfile,
)


@pytest.mark.django_db
class TestModels:
    def test_user_profile_creation(self):
        user = User.objects.create_user(username="testuser", password="password")
        # Ensure signal creates UserProfile
        profile = UserProfile.objects.get(user=user)
        assert profile.is_coach is False
        assert str(profile) == "testuser (Користувач)"

        profile.is_coach = True
        profile.save()
        assert str(profile) == "testuser (Тренер)"

    def test_player_creation_and_rating(self):
        user = User.objects.create_user(username="player1", password="password")
        player = Player.objects.create(user=user, position="FWD", jersey_number=10)
        assert str(player) == "player1 - Нападник"
        assert player.calculate_rating() == Decimal("0.00")

    def test_player_stats_and_rating_update(self):
        user = User.objects.create_user(username="player2", password="password")
        player = Player.objects.create(user=user, position="FWD", jersey_number=9)
        stats = PlayerStats.objects.create(
            player=player, match_id=1, goals=2, shots_on_target=3, minutes_played=90
        )
        # Rating should be calculated:
        # Base(5.0) + Goals(2*1.0) + ShotsOnTarget(min(3*0.2, 1.5)=0.6) = 7.6
        assert stats.rating == Decimal("7.6")
        assert str(stats) == "player2 - Матч 1"

        player.refresh_from_db()
        assert player.matches_played == 1
        assert player.overall_rating == Decimal("7.60")

        # History should be updated
        history = PlayerRatingHistory.objects.filter(player=player).first()
        assert history is not None
        assert history.rating == Decimal("7.60")
        assert f"player2 - 7.60" == str(history)

    def test_upl_squad_cache(self):
        import django.utils.timezone as timezone

        cache = UPLSquadCache.objects.create(
            team_name="Dynamo Kyiv",
            api_team_id=123,
            squad_json=[{"id": 1, "name": "Player 1"}],
            fetched_at=timezone.now(),
        )
        assert "Dynamo Kyiv" in str(cache)

    def test_tournament(self):
        tour = Tournament.objects.create(
            name="Champions League",
            start_date="2025-01-01",
            end_date="2025-12-31",
            format="Group + Knockout",
            max_teams=32,
            location="Europe",
        )
        assert str(tour) == "Champions League"

    def test_team(self):
        tour = Tournament.objects.create(
            name="Local Cup",
            start_date="2025-01-01",
            end_date="2025-12-31",
            format="Knockout",
            max_teams=16,
            location="City",
        )
        team = Team.objects.create(
            tournament=tour,
            name="FC Local",
            captain="John Doe",
            email="contact@local.fc",
            phone="123456789",
        )
        assert str(team) == "FC Local (Local Cup)"

    def test_match(self):
        tour = Tournament.objects.create(
            name="Local Cup 2",
            start_date="2025-01-01",
            end_date="2025-12-31",
            format="Knockout",
            max_teams=16,
            location="City 2",
        )
        match = Match.objects.create(
            tournament=tour,
            date="2025-02-01T15:00:00Z",
            home_team="Team A",
            away_team="Team B",
            home_score=2,
            away_score=1,
        )
        assert match.home_team == "Team A"
        assert match.home_score == 2
