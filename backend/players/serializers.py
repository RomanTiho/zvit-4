from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Player, PlayerStats, PlayerRatingHistory


class UserSerializer(serializers.ModelSerializer):
    """Serializer для користувача"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PlayerStatsSerializer(serializers.ModelSerializer):
    """Serializer для статистики гравця"""
    class Meta:
        model = PlayerStats
        fields = ['id', 'match_id', 'goals', 'assists', 'yellow_cards', 
                  'red_cards', 'minutes_played', 'rating', 'created_at']
        read_only_fields = ['rating', 'created_at']


class PlayerRatingHistorySerializer(serializers.ModelSerializer):
    """Serializer для історії рейтингу"""
    class Meta:
        model = PlayerRatingHistory
        fields = ['rating', 'recorded_at']


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer для гравця"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    recent_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'position', 'overall_rating', 
                  'matches_played', 'recent_stats', 'created_at', 'updated_at']
        read_only_fields = ['overall_rating', 'matches_played', 'created_at', 'updated_at']
    
    def get_recent_stats(self, obj):
        """Отримати останні 5 матчів"""
        recent = obj.stats.all()[:5]
        return PlayerStatsSerializer(recent, many=True).data


class PlayerDetailSerializer(PlayerSerializer):
    """Детальний serializer для гравця"""
    user = UserSerializer(read_only=True)
    rating_history = PlayerRatingHistorySerializer(many=True, read_only=True)
    all_stats = PlayerStatsSerializer(source='stats', many=True, read_only=True)
    
    class Meta(PlayerSerializer.Meta):
        fields = PlayerSerializer.Meta.fields + ['user', 'rating_history', 'all_stats']
