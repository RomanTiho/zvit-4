from rest_framework import serializers
from django.contrib.auth.models import User
# Імпорт буде з players_models.py після інтеграції


class PlayerStatsSerializer(serializers.Serializer):
    """Serializer для статистики гравця"""
    id = serializers.IntegerField(read_only=True)
    match_id = serializers.IntegerField()
    goals = serializers.IntegerField(default=0)
    assists = serializers.IntegerField(default=0)
    yellow_cards = serializers.IntegerField(default=0)
    red_cards = serializers.IntegerField(default=0)
    minutes_played = serializers.IntegerField(default=90)
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class PlayerSerializer(serializers.Serializer):
    """Serializer для гравця"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    position = serializers.ChoiceField(choices=[
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward')
    ])
    overall_rating = serializers.DecimalField(max_digits=4, decimal_places=2, read_only=True)
    matches_played = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
