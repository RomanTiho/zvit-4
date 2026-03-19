from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Player, PlayerStats, PlayerRatingHistory, Tournament, Team, Standing, Match, UserProfile


class UserAdmin(BaseUserAdmin):
    """Стандартна адмінка User з групами"""
    pass

# Перереєстрація User (стандартна адмінка вже підтримує групи)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_groups')
    search_fields = ('user__username', 'user__email')

    def get_groups(self, obj):
        return ', '.join(obj.user.groups.values_list('name', flat=True)) or 'Користувач'
    get_groups.short_description = 'Ролі'


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'format')
    list_filter = ('status', 'format')
    search_fields = ('name', 'location')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'captain', 'email', 'status')
    list_filter = ('tournament', 'status')
    search_fields = ('name', 'captain')
    actions = ['approve_teams', 'reject_teams']

    @admin.action(description='Підтвердити вибрані заявки')
    def approve_teams(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'Підтверджено {updated} заявок обо команд.')

    @admin.action(description='Відхилити вибрані заявки')
    def reject_teams(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Відхилено {updated} заявок.')

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
