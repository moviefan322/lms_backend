from rest_framework import serializers
from core.models import Team, TeamSeason, TeamPlayer
from player.serializers import PlayerSerializer


class TeamPlayerSerializer(serializers.ModelSerializer):
    """Serializer for the TeamPlayer model."""
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = TeamPlayer
        fields = ['id', 'player', 'handicap', 'wins', 'losses', 'is_active']
        read_only_fields = ['id']


class TeamSeasonSerializer(serializers.ModelSerializer):
    """Serializer for the TeamSeason model."""
    captain = PlayerSerializer(read_only=True)
    team_players = TeamPlayerSerializer(many=True, read_only=True)

    class Meta:
        model = TeamSeason
        fields = ['id', 'name', 'captain', 'wins', 'losses',
                  'games_won', 'games_lost', 'team_players']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for the Team model."""
    team_season = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'league', 'team_season']

    def get_team_season(self, obj):
        team_season = TeamSeason.objects.filter(team=obj).first()
        return TeamSeasonSerializer(team_season).data if team_season else None
