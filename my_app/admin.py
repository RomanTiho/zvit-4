from django.contrib import admin
from .models import Player, PlayerStats, PlayerRatingHistory, Tournament, Team, Standing, Match

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'format')
    list_filter = ('status', 'format')
    search_fields = ('name', 'location')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'captain', 'email')
    list_filter = ('tournament',)
    search_fields = ('name', 'captain')

@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    list_display = ('team', 'tournament', 'played', 'points')
    list_filter = ('tournament',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'home_score', 'away_score', 'date', 'status')
    list_filter = ('tournament', 'status')


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
