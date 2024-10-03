from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import TeamSeason, TeamPlayer, Player
from player import serializers
from .permissions import IsAdminOrReadOnly


class PlayerViewSet(viewsets.ModelViewSet):
    """View for managing player APIs."""
    serializer_class = serializers.PlayerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Return players for admin or players in the same league."""
        user = self.request.user

        # Admins can view all players
        if user.is_admin:
            return Player.objects.all().order_by('name')

        # Regular users can see players from the same league
        if user.is_active and user.player_profile:
            leagues = user.player_profile.teams.values('season__league')
            return Player.objects.filter(
                team_players__team_season__season__league__in=leagues
            ).distinct()

        # If the user has no player profile or isn't in a league, return empty
        return Player.objects.none()

    def perform_create(self, serializer):
        """Create a new player (only for admin users)."""
        player = serializer.save()

        # If 'team_season' is provided, associate the player with the team
        team_season_id = self.request.data.get('team_season')
        if team_season_id:
            try:
                team_season = TeamSeason.objects.get(id=team_season_id)
                TeamPlayer.objects.create(
                    player=player, team_season=team_season)
            except TeamSeason.DoesNotExist:
                raise serializers.ValidationError("Invalid team_season ID")
