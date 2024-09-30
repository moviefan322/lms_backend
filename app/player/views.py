from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.models import Player, League, Team
from player import serializers
from .permissions import IsAdminOrReadOnly


class PlayerViewSet(viewsets.ModelViewSet):
    """View for managing player APIs."""
    serializer_class = serializers.PlayerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Return players for admin or a player."""
        user = self.request.user

        if user.is_admin:
            return Player.objects.all().order_by('name')

        if not user.is_active or not user.player_profile:
            return Player.objects.none()

        player_leagues = League.objects.filter(
            seasons__teamseason__team_players__player=user.player_profile
        ).distinct()

        teams = Team.objects.filter(
            league__in=player_leagues
        ).order_by('name').distinct()

        return teams
    
    def perform_create(self, serializer):
        """Create a new team."""
        serializer.save()

    def perform_update(self, serializer):
        """Update a team if the user is authorized."""
        serializer.save()