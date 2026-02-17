from decimal import Decimal
from django.db.models import Sum, Avg
from .models import Player, PlayerStats, PlayerRatingHistory


class PlayerRatingService:
    """Сервіс для розрахунку рейтингу гравців"""
    
    # Ваги для різних статистик
    WEIGHTS = {
        'goals': Decimal('3.0'),
        'assists': Decimal('2.0'),
        'yellow_cards': Decimal('-1.0'),
        'red_cards': Decimal('-3.0'),
    }
    
    @staticmethod
    def calculate_rating(player):
        """
        Розрахунок рейтингу на основі статистики
        
        Args:
            player: об'єкт Player
            
        Returns:
            Decimal: новий рейтинг гравця
        """
        stats = PlayerStats.objects.filter(player=player)
        
        if not stats.exists():
            return Decimal('0.00')
        
        total_rating = Decimal('0')
        
        for stat in stats:
            # Базовий рейтинг за матч
            match_rating = Decimal('5.0')
            
            # Додаємо бали за голи та асисти
            match_rating += stat.goals * PlayerRatingService.WEIGHTS['goals']
            match_rating += stat.assists * PlayerRatingService.WEIGHTS['assists']
            
            # Віднімаємо за картки
            match_rating += stat.yellow_cards * PlayerRatingService.WEIGHTS['yellow_cards']
            match_rating += stat.red_cards * PlayerRatingService.WEIGHTS['red_cards']
            
            # Нормалізація рейтингу (1-10)
            match_rating = max(Decimal('1.0'), min(Decimal('10.0'), match_rating))
            
            # Зберігаємо рейтинг матчу
            if stat.rating != match_rating:
                stat.rating = match_rating
                stat.save(update_fields=['rating'])
            
            total_rating += match_rating
        
        # Середній рейтинг
        new_rating = total_rating / len(stats)
        new_rating = round(new_rating, 2)
        
        # Оновлення рейтингу гравця
        player.overall_rating = new_rating
        player.matches_played = len(stats)
        player.save(update_fields=['overall_rating', 'matches_played'])
        
        # Збереження в історію
        PlayerRatingHistory.objects.create(
            player=player,
            rating=new_rating
        )
        
        return new_rating
    
    @staticmethod
    def get_player_statistics(player):
        """
        Отримати детальну статистику гравця
        
        Args:
            player: об'єкт Player
            
        Returns:
            dict: статистика гравця
        """
        stats = PlayerStats.objects.filter(player=player)
        
        if not stats.exists():
            return {
                'total_goals': 0,
                'total_assists': 0,
                'total_yellow_cards': 0,
                'total_red_cards': 0,
                'avg_rating': 0,
                'matches_played': 0
            }
        
        aggregated = stats.aggregate(
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            total_yellow_cards=Sum('yellow_cards'),
            total_red_cards=Sum('red_cards'),
            avg_rating=Avg('rating')
        )
        
        return {
            'total_goals': aggregated['total_goals'] or 0,
            'total_assists': aggregated['total_assists'] or 0,
            'total_yellow_cards': aggregated['total_yellow_cards'] or 0,
            'total_red_cards': aggregated['total_red_cards'] or 0,
            'avg_rating': round(float(aggregated['avg_rating'] or 0), 2),
            'matches_played': stats.count()
        }
