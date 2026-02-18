from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    """Модель гравця з рейтингом"""
    POSITION_CHOICES = [
        ('GK', 'Воротар'),
        ('DEF', 'Захисник'),
        ('MID', 'Півзахисник'),
        ('FWD', 'Нападник')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    jersey_number = models.IntegerField(null=True, blank=True, help_text='Ігровий номер (1-99)')
    overall_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    matches_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_rating']
        verbose_name = 'Гравець'
        verbose_name_plural = 'Гравці'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"
    
    def calculate_rating(self):
        """Розрахунок рейтингу на основі статистики останніх матчів"""
        from django.db.models import Avg
        from decimal import Decimal
        
        # Беремо останні 10 матчів
        recent_stats = self.stats.all()[:10]
        
        if not recent_stats.exists():
            return Decimal('50.0')  # Базовий рейтинг для нових гравців
        
        # Середній рейтинг за матчі
        avg_match_rating = recent_stats.aggregate(Avg('rating'))['rating__avg'] or Decimal('5.0')
        base_rating = Decimal(str(avg_match_rating)) * Decimal('10')  # Конвертуємо з 0-10 в 0-100
        
        # Бонуси за результативність
        total_goals = sum(stat.goals for stat in recent_stats)
        total_assists = sum(stat.assists for stat in recent_stats)
        
        # Різні бонуси для різних позицій
        if self.position == 'FWD':
            goals_bonus = Decimal(str(total_goals)) * Decimal('2.0')
            assists_bonus = Decimal(str(total_assists)) * Decimal('1.0')
        elif self.position == 'MID':
            goals_bonus = Decimal(str(total_goals)) * Decimal('1.5')
            assists_bonus = Decimal(str(total_assists)) * Decimal('1.5')
        elif self.position == 'DEF':
            goals_bonus = Decimal(str(total_goals)) * Decimal('1.0')
            assists_bonus = Decimal(str(total_assists)) * Decimal('1.0')
        else:  # GK
            goals_bonus = Decimal('0')
            assists_bonus = Decimal('0')
        
        # Штрафи за картки
        total_yellow = sum(stat.yellow_cards for stat in recent_stats)
        total_red = sum(stat.red_cards for stat in recent_stats)
        cards_penalty = (Decimal(str(total_yellow)) * Decimal('0.5')) + (Decimal(str(total_red)) * Decimal('3.0'))
        
        # Фінальний рейтинг
        final_rating = base_rating + goals_bonus + assists_bonus - cards_penalty
        
        # Обмежуємо від 0 до 100
        final_rating = max(Decimal('0'), min(final_rating, Decimal('100')))
        return round(final_rating, 2)
    
    def update_rating(self):
        """Оновити рейтинг гравця"""
        new_rating = self.calculate_rating()
        
        # Зберегти в історію якщо рейтинг змінився
        if self.overall_rating != new_rating:
            PlayerRatingHistory.objects.create(
                player=self,
                rating=new_rating
            )
            self.overall_rating = new_rating
            self.save()
        
        return new_rating


class PlayerStats(models.Model):
    """Статистика гравця за матч"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='stats')
    match_id = models.IntegerField()
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=90)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статистика гравця'
        verbose_name_plural = 'Статистика гравців'
    
    def __str__(self):
        return f"{self.player.user.username} - Матч {self.match_id}"
    
    def save(self, *args, **kwargs):
        """При збереженні статистики оновлюємо рейтинг гравця"""
        super().save(*args, **kwargs)
        # Оновлюємо кількість матчів
        self.player.matches_played = self.player.stats.count()
        self.player.save()
        # Перераховуємо рейтинг
        self.player.update_rating()


class PlayerRatingHistory(models.Model):
    """Історія зміни рейтингу"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='rating_history')
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Історія рейтингу'
        verbose_name_plural = 'Історія рейтингів'
    
    def __str__(self):
        return f"{self.player.user.username} - {self.rating}"
