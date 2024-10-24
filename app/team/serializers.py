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
    team_players = TeamPlayerSerializer(many=True, read_only=True)
    
    class Meta:
        model = TeamSeason
        fields = ['id', 'team', 'season', 'captain', 'team_players'] 
        read_only_fields = ['id', 'name', 'wins', 'losses', 'games_won', 'games_lost']

    def create(self, validated_data):
        """Override the create method to handle defaults."""
        team = validated_data['team']
        name = team.name  # Set name from the team
        validated_data['name'] = name  # Auto-fill name
        validated_data['wins'] = 0
        validated_data['losses'] = 0
        validated_data['games_won'] = 0
        validated_data['games_lost'] = 0
        return super().create(validated_data)



class TeamSerializer(serializers.ModelSerializer):
    """Serializer for the Team model."""
    team_season = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'league', 'team_season']

    def get_team_season(self, obj):
        team_season = TeamSeason.objects.filter(team=obj).first()
        return TeamSeasonSerializer(team_season).data if team_season else None
