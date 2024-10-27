from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from core.models import Team, League, TeamSeason, TeamPlayer
from team import serializers
from .permissions import IsAdminOrReadOnly


class TeamPlayerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing TeamPlayer API requests."""
    serializer_class = serializers.TeamPlayerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Filter TeamPlayer by teamseason_id."""
        team_season_id = self.kwargs['teamseason_id']
        return TeamPlayer.objects.filter(team_season_id=team_season_id)

    def perform_create(self, serializer):
        team_season_id = self.kwargs['teamseason_id']
        team_season = get_object_or_404(TeamSeason, id=team_season_id)
        serializer.save(team_season=team_season)

    def perform_update(self, serializer):
        team_player_id = self.kwargs['pk']

        team_player = get_object_or_404(TeamPlayer, id=team_player_id)
        player = team_player.player

        serializer.save(player=player)


class TeamViewSet(viewsets.ModelViewSet):
    """View for managing team APIs."""
    serializer_class = serializers.TeamSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Return teams for admin or a player, filtered by league."""
        user = self.request.user
        league_id = self.kwargs['league_id']  # Get league_id from the URL
        league = League.objects.filter(id=league_id).first()

        if user.is_admin:
            # Admin can access all teams in the league
            return Team.objects.filter(league=league).order_by('name')

        if not user.is_active or not user.player_profile:
            # No access if the user is inactive or has no profile
            return Team.objects.none()

        # Find leagues where the user is a player
        player_leagues = League.objects.filter(
            seasons__teamseason__team_players__player=user.player_profile
        ).distinct()

        # Return teams only from the player's leagues
        teams = Team.objects.filter(
            league__in=player_leagues, league=league
        ).order_by('name').distinct()

        return teams

    def perform_create(self, serializer):
        """Create a new team in the given league."""
        league_id = self.kwargs['league_id']  # Get league_id from the URL
        league = League.objects.get(id=league_id)
        serializer.save(league=league)  # Save team under the correct league

    def perform_update(self, serializer):
        """Update a team if the user is authorized."""
        serializer.save()
