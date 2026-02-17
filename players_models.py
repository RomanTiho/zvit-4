from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    """Модель гравця з рейтингом"""
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    overall_rating = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    matches_played = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-overall_rating']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"


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
    
    def __str__(self):
        return f"{self.player.user.username} - Match {self.match_id}"


class PlayerRatingHistory(models.Model):
    """Історія зміни рейтингу"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='rating_history')
    rating = models.DecimalField(max_digits=4, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.player.user.username} - {self.rating}"
