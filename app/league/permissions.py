from rest_framework import permissions
from core.models import (
    League,
    Season,
    Schedule,
    MatchNight,
    Match,
    Game
)


class IsAdminOrLeagueMember(permissions.BasePermission):
    """Custom permission to allow full access to
    league admins and additional admins,
    and read-only access to members of the league (players)."""

    def has_permission(self, request, view):
        """Check permission at the view level."""
        league = self.get_league_from_request(view)

        if not league:
            return request.user.is_admin

        is_admin_or_additional = (
            request.user == league.admin or
            request.user in league.additional_admins.all()
        )

        if is_admin_or_additional:
            return True

        if request.method in permissions.SAFE_METHODS:
            return self.is_user_in_league(request.user, league)

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for each specific object."""
        league = self.get_league_from_object(obj)

        if not league:
            return False

        if request.method in permissions.SAFE_METHODS:
            return self.is_user_in_league(request.user, league)

        is_admin_or_additional = (
            request.user == league.admin or
            request.user in league.additional_admins.all()
        )
        return is_admin_or_additional

    def is_user_in_league(self, user, league):
        """Check if a user is part of a league
        either as admin, additional admin, or player."""
        if user == league.admin or user in league.additional_admins.all():
            return True

        # Check if the user is a player in any team associated with this league
        is_player_in_league = Season.objects.filter(
            league=league,
            teamseason__players=user.player_profile
        ).exists()
        return is_player_in_league

    def get_league_from_request(self, view):
        """Helper function to retrieve league from view kwargs."""
        if 'league_id' in view.kwargs:
            return League.objects.filter(pk=view.kwargs['league_id']).first()
        elif 'season_id' in view.kwargs:
            season = Season.objects.filter(pk=view.kwargs['season_id']).first()
            return season.league if season else None
        elif 'pk' in view.kwargs:
            return League.objects.filter(pk=view.kwargs['pk']).first()
        return None

    def get_league_from_object(self, obj):
        """Helper function to retrieve league
        from an object (Match, Schedule, etc.)."""
        if isinstance(obj, League):
            return obj
        elif isinstance(obj, Season):
            return obj.league
        elif isinstance(obj, Schedule):
            return obj.season.league
        elif isinstance(obj, MatchNight):
            return obj.schedule.season.league
        elif isinstance(obj, Match):
            return obj.match_night.schedule.season.league
        elif isinstance(obj, Game):
            return obj.match.match_night.schedule.season.league
        return None
