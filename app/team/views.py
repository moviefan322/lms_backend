from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Team, League, TeamSeason
from team import serializers
from .permissions import IsAdminOrReadOnly


class TeamViewSet(viewsets.ModelViewSet):
    """View for managing team APIs."""
    serializer_class = serializers.TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Return teams for admin or a player."""
        user = self.request.user

        if user.is_admin:
            return Team.objects.all().order_by('name')

        if not user.is_active or not user.player_profile:
            return Team.objects.none()

        player_leagues = League.objects.filter(
            teams__teamseason__players=user.player_profile
        ).distinct()

        return Team.objects.filter(
            league__in=player_leagues
        ).order_by('name').distinct()

    def perform_create(self, serializer):
        """Create a new team."""
        serializer.save()

    def perform_update(self, serializer):
        """Update a team if the user is authorized."""
        serializer.save()


class TeamSeasonViewSet(viewsets.ModelViewSet):
    """View for managing TeamSeason API requests."""
    queryset = TeamSeason.objects.all()
    serializer_class = serializers.TeamSeasonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter team season by team or season if provided."""
        queryset = self.queryset

        team_id = self.request.query_params.get('team_id')
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        season_id = self.request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(season_id=season_id)

        return queryset
