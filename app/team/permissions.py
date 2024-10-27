from rest_framework import permissions
from core.models import League, TeamSeason, TeamPlayer


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission for allowing league admins
    or league players to access data."""

    def has_permission(self, request, view):
        # Read-only access for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Get league_id from URL kwargs
        league_id = view.kwargs.get('league_id')
        if not league_id:
            return False

        try:
            league = League.objects.get(pk=league_id)
        except League.DoesNotExist:
            return False

        # Check if user is an admin or additional admin of the league
        return (
            request.user.is_authenticated and
            request.user.is_active and
            (
                request.user == league.admin or
                request.user in league.additional_admins.all()
            )
        )

    def has_object_permission(self, request, view, obj):
        """Object-level permissions for TeamPlayer and related instances."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        league = None

        if isinstance(obj, TeamPlayer):
            league = obj.team_season.team.league
        elif isinstance(obj, TeamSeason):
            league = obj.team.league
        elif hasattr(obj, 'league'):
            league = obj.league

        if not league:
            return False

        is_admin = request.user == league.admin
        is_additional_admin = request.user in league.additional_admins.all()

        if is_admin or is_additional_admin:
            return True

        return hasattr(
            request.user, 'player_profile'
            ) and request.user.player_profile in [
            player.player for season in league.seasons.all()
            for player in season.teamseason_set.all()
        ]
