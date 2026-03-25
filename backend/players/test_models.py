from decimal import Decimal

from django.contrib.auth.models import User

import pytest

from .models import Player, PlayerRatingHistory, PlayerStats


@pytest.mark.django_db
class TestPlayerModels:
    def test_str_methods(self):
        user = User.objects.create_user(username="ronaldo", password="123")
        player = Player.objects.create(
            user=user, position="FWD", overall_rating=Decimal("8.5")
        )
        assert str(player) == "ronaldo - Forward"

        stats = PlayerStats.objects.create(player=player, match_id=10, goals=2)
        assert str(stats) == "ronaldo - Match 10"

        history = PlayerRatingHistory.objects.create(
            player=player, rating=Decimal("9.0")
        )
        assert "ronaldo - 9.0" in str(history)
