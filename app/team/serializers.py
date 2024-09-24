from rest_framework import serializers
from core.models import TeamSeason, Team, TeamPlayer
from player.serializers import PlayerSerializer


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for the Team model."""

    class Meta:
        model = Team
        fields = ['id', 'name', 'league']


class TeamPlayerSerializer(serializers.ModelSerializer):
    """Serializer for the TeamPlayer model."""
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = TeamPlayer
        fields = ['id', 'player', 'handicap', 'wins', 'losses', 'is_active']
        read_only_fields = ['id']


class TeamSeasonSerializer(serializers.ModelSerializer):
    """Serializer for the TeamSeason model."""
    team = TeamSerializer(read_only=True)
    captain = PlayerSerializer(read_only=True)
    team_players = TeamPlayerSerializer(
        many=True, source='teamplayer_set', read_only=True)

    class Meta:
        model = TeamSeason
        fields = ['id', 'team', 'season', 'captain', 'wins',
                  'losses', 'games_won', 'games_lost', 'team_players']
        read_only_fields = ['id', 'season']
