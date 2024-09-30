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
        """Return players for admin or the authenticated player."""
        user = self.request.user

        if user.is_admin:
            return Player.objects.all().order_by('name')

        if not user.is_active or not hasattr(user, 'player_profile'):
            return Player.objects.none()

        return Player.objects.filter(player_profile=user.player_profile)

    def perform_create(self, serializer):
        """Create a new player, optionally associating with a TeamSeason."""
        player = serializer.save()

        # Check if 'team_season' was provided, and associate player with it
        team_season_id = self.request.data.get('team_season')
        if team_season_id:
            try:
                team_season = TeamSeason.objects.get(id=team_season_id)
                TeamPlayer.objects.create(
                    player=player, team_season=team_season)
            except TeamSeason.DoesNotExist:
                raise serializers.ValidationError("Invalid team_season ID")
