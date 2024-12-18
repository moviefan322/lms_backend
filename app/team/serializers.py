from rest_framework import serializers
from core.models import Team, TeamSeason, TeamPlayer, Player


class TeamPlayerSerializer(serializers.ModelSerializer):
    """Serializer for the TeamPlayer model."""
    player = serializers.PrimaryKeyRelatedField(queryset=Player.objects.all())
    name = serializers.SerializerMethodField()

    class Meta:
        model = TeamPlayer
        fields = ['id', 'player', 'name', 'handicap',
                  'is_active', 'wins', 'losses']
        read_only_fields = ['id', 'name']
        extra_kwargs = {
            'handicap': {'required': False},
            'wins': {'required': False},
            'losses': {'required': False},
            'is_active': {'default': True},
        }

    def get_name(self, obj):
        return obj.player.name

    def create(self, validated_data):
        validated_data.setdefault('is_active', True)
        validated_data['wins'] = 0
        validated_data['losses'] = 0

        player = validated_data.get('player')
        if 'handicap' not in validated_data:
            last_record = TeamPlayer.objects.filter(
                player=player).order_by('-created_at').first()
            validated_data[
                'handicap'] = last_record.handicap if last_record else 3

        return super().create(validated_data)


class TeamSeasonSerializer(serializers.ModelSerializer):
    """Serializer for the TeamSeason model."""
    team_players = TeamPlayerSerializer(many=True, read_only=True)
    name = serializers.CharField(required=False)
    captain = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(), required=False)
    captain_name = serializers.SerializerMethodField()

    class Meta:
        model = TeamSeason
        fields = ['id', 'name', 'team', 'season',
                  'captain', 'captain_name', 'team_players']
        read_only_fields = ['id', 'wins', 'losses', 'games_won', 'games_lost']

    def get_captain_name(self, obj):
        """Fetch captain's name if captain exists."""
        return obj.captain.name if obj.captain else None

    def create(self, validated_data):
        """Override the create method to handle defaults."""
        team = validated_data['team']

        validated_data['name'] = validated_data.get('name', team.name)
        # Initialize other fields
        validated_data['wins'] = 0
        validated_data['losses'] = 0
        validated_data['games_won'] = 0
        validated_data['games_lost'] = 0
        return super().create(validated_data)


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for the Team model."""
    team_season = TeamSeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'league', 'team_season']

    def get_team_season(self, obj):
        team_seasons = TeamSeason.objects.filter(
            team=obj).order_by('-created_at')
        return TeamSeasonSerializer(team_seasons, many=True).data
