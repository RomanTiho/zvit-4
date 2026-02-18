from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Player, PlayerStats, PlayerRatingHistory


class UserSerializer(serializers.ModelSerializer):
    """Serializer для користувача"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer для реєстрації нового користувача"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    position = serializers.ChoiceField(choices=Player.POSITION_CHOICES, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'first_name', 'last_name', 'position']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Паролі не співпадають."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        position = validated_data.pop('position', 'MID')  # Default position
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        
        # Автоматично створити профіль гравця
        Player.objects.create(user=user, position=position)
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer для профілю користувача"""
    player = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'player']
        read_only_fields = ['username']
    
    def get_player(self, obj):
        try:
            player = obj.player
            return {
                'id': player.id,
                'position': player.position,
                'jersey_number': player.jersey_number,
                'overall_rating': float(player.overall_rating),
                'matches_played': player.matches_played
            }
        except Player.DoesNotExist:
            return None


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer для оновлення профілю"""
    position = serializers.ChoiceField(choices=Player.POSITION_CHOICES, required=False)
    jersey_number = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=99)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'position', 'jersey_number']
    
    def update(self, instance, validated_data):
        position = validated_data.pop('position', None)
        jersey_number = validated_data.pop('jersey_number', None)
        
        # Оновити дані користувача
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        
        # Оновити позицію та номер гравця
        if position or jersey_number is not None:
            try:
                player = instance.player
                if position:
                    player.position = position
                if jersey_number is not None:
                    player.jersey_number = jersey_number
                player.save()
            except Player.DoesNotExist:
                Player.objects.create(
                    user=instance, 
                    position=position or 'MID',
                    jersey_number=jersey_number
                )
        
        return instance


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
        fields = ['id', 'username', 'email', 'position', 'jersey_number', 'overall_rating', 
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
