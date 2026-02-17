from django.contrib import admin
from .models import Player, PlayerStats, PlayerRatingHistory


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'overall_rating', 'matches_played', 'created_at']
    list_filter = ['position', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['overall_rating', 'matches_played', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('user', 'position')
        }),
        ('Рейтинг', {
            'fields': ('overall_rating', 'matches_played')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'match_id', 'goals', 'assists', 'rating', 'created_at']
    list_filter = ['created_at']
    search_fields = ['player__user__username']
    readonly_fields = ['rating', 'created_at']
    
    fieldsets = (
        ('Матч', {
            'fields': ('player', 'match_id')
        }),
        ('Статистика', {
            'fields': ('goals', 'assists', 'yellow_cards', 'red_cards', 'minutes_played')
        }),
        ('Рейтинг', {
            'fields': ('rating', 'created_at')
        }),
    )


@admin.register(PlayerRatingHistory)
class PlayerRatingHistoryAdmin(admin.ModelAdmin):
    list_display = ['player', 'rating', 'recorded_at']
    list_filter = ['recorded_at']
    search_fields = ['player__user__username']
    readonly_fields = ['recorded_at']
    date_hierarchy = 'recorded_at'
