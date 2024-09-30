from rest_framework import serializers
from core.models import Player, TeamSeason


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for the Player model."""

    class Meta:
        model = Player
        fields = ['id', 'name', 'is_active']
        read_only_fields = ['id', 'user']


class PlayerDetailSerializer(PlayerSerializer):
    """Serializer for the Player model detail view."""

    class Meta:
        model = Player
        fields = ['id', 'name', 'is_active']
        read_only_fields = ['id']

    def get_teams(self, obj):
        """Return the teams for the player via TeamPlayer intermediary."""
        team_seasons = obj.team_players.values_list('team_season', flat=True)
        return list(team_seasons)