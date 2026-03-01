from decimal import Decimal
from django.db.models import Sum, Avg
from .models import Player, PlayerStats, PlayerRatingHistory


class PlayerRatingService:
    """Сервіс для розрахунку рейтингу гравців"""

    @staticmethod
    def calculate_rating(player):
        """
        Розраховує overall_rating гравця як середнє рейтингів матчів (шкала 1.0–10.0).
        Рейтинг кожного матчу вже розраховується автоматично в PlayerStats._calculate_match_rating().

        Args:
            player: об'єкт Player
        Returns:
            Decimal: новий overall_rating гравця
        """
        stats = PlayerStats.objects.filter(player=player).exclude(rating__isnull=True)

        if not stats.exists():
            return Decimal('0.00')

        avg = stats.aggregate(avg=Avg('rating'))['avg'] or Decimal('0')
        new_rating = round(Decimal(str(avg)), 2)

        # Зберігаємо в полі гравця
        player.overall_rating = new_rating
        player.save(update_fields=['overall_rating'])

        # Додаємо запис в історію
        PlayerRatingHistory.objects.create(player=player, rating=new_rating)

        return new_rating

    @staticmethod
    def get_player_statistics(player):
        """
        Повна зведена статистика гравця по всіх матчах.

        Returns:
            dict: агрегована статистика
        """
        stats = PlayerStats.objects.filter(player=player)

        if not stats.exists():
            return {
                'total_goals': 0,
                'total_assists': 0,
                'total_shots': 0,
                'total_shots_on_target': 0,
                'total_key_passes': 0,
                'total_saves': 0,
                'total_tackles': 0,
                'total_interceptions': 0,
                'total_yellow_cards': 0,
                'total_red_cards': 0,
                'avg_rating': 0,
                'matches_played': 0,
            }

        agg = stats.aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            total_shots=Sum('shots'),
            total_shots_on_target=Sum('shots_on_target'),
            total_key_passes=Sum('key_passes'),
            total_saves=Sum('saves'),
            total_tackles=Sum('tackles'),
            total_interceptions=Sum('interceptions'),
            total_yellow_cards=Sum('yellow_cards'),
            total_red_cards=Sum('red_cards'),
            avg_rating=Avg('rating'),
        )

        return {
            'total_goals':          agg['total_goals'] or 0,
            'total_assists':        agg['total_assists'] or 0,
            'total_shots':          agg['total_shots'] or 0,
            'total_shots_on_target':agg['total_shots_on_target'] or 0,
            'total_key_passes':     agg['total_key_passes'] or 0,
            'total_saves':          agg['total_saves'] or 0,
            'total_tackles':        agg['total_tackles'] or 0,
            'total_interceptions':  agg['total_interceptions'] or 0,
            'total_yellow_cards':   agg['total_yellow_cards'] or 0,
            'total_red_cards':      agg['total_red_cards'] or 0,
            'avg_rating':           round(float(agg['avg_rating'] or 0), 2),
            'matches_played':       stats.count(),
        }
