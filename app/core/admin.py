"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['id', 'email', 'name']  # Include 'id' here
    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['id', 'last_login']  # Mark 'id' as read-only
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )


class LeagueAdmin(admin.ModelAdmin):
    """Admin for League."""
    list_display = ['name', 'admin', 'is_active']
    search_fields = ['name', 'admin__email']
    list_filter = ['is_active']


class SeasonAdmin(admin.ModelAdmin):
    """Admin for Season."""
    list_display = ['name', 'year', 'league', 'is_active']
    list_filter = ['league', 'year', 'is_active']
    search_fields = ['name', 'league__name']


class TeamAdmin(admin.ModelAdmin):
    """Admin for Team."""
    list_display = ['name', 'league']
    search_fields = ['name', 'league__name']
    list_filter = ['league']


class TeamSeasonAdmin(admin.ModelAdmin):
    """Admin for TeamSeason."""
    list_display = ['team', 'season', 'captain',
                    'wins', 'losses', 'get_team_players']
    search_fields = ['team__name', 'season__name']
    list_filter = ['season']

    def get_team_players(self, obj):
        # Access team_players correctly if related_name is set
        return ", ".join([
            player.player.name for player in obj.team_players.all()])

    get_team_players.short_description = 'Team Players'


class PlayerAdmin(admin.ModelAdmin):
    """Admin for Player."""
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


class TeamPlayerAdmin(admin.ModelAdmin):
    """Admin for TeamPlayer."""
    list_display = ['team_season', 'player',
                    'handicap', 'wins', 'losses', 'is_captain']
    search_fields = ['player__name', 'team_season__team__name']
    list_filter = ['team_season', 'is_captain']


class ScheduleAdmin(admin.ModelAdmin):
    """Admin for Schedule."""
    list_display = ['season', 'start_date', 'num_weeks']
    list_filter = ['season']
    search_fields = ['season__name']


class MatchNightAdmin(admin.ModelAdmin):
    """Admin for MatchNight."""
    list_display = ['schedule', 'date', 'status']
    list_filter = ['schedule', 'status']
    search_fields = ['schedule__season__name']


class MatchAdmin(admin.ModelAdmin):
    """Admin for Match."""
    list_display = ['match_night', 'home_team',
                    'away_team', 'home_score', 'away_score', 'status']
    search_fields = ['home_team__team__name', 'away_team__team__name']
    list_filter = ['status', 'match_night__schedule__season']


class GameAdmin(admin.ModelAdmin):
    """Admin for Game."""
    list_display = ['match', 'home_player', 'away_player',
                    'home_score', 'away_score', 'status']
    search_fields = ['home_player__player__name', 'away_player__player__name']
    list_filter = ['status']


# Register the models
admin.site.register(models.User, UserAdmin)
admin.site.register(models.League, LeagueAdmin)
admin.site.register(models.Season, SeasonAdmin)
admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.TeamSeason, TeamSeasonAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.TeamPlayer, TeamPlayerAdmin)
admin.site.register(models.Schedule, ScheduleAdmin)
admin.site.register(models.MatchNight, MatchNightAdmin)
admin.site.register(models.Match, MatchAdmin)
admin.site.register(models.Game, GameAdmin)
