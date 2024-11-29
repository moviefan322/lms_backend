from rest_framework import serializers
from team.serializers import TeamSeasonSerializer
from core.models import (
    League,
    Season,
    Schedule,
    MatchNight,
    Match,
    Game,
)


class GameSerializer(serializers.ModelSerializer):
    """Serializer for the Game model."""
    match = serializers.PrimaryKeyRelatedField(queryset=Match.objects.all())

    class Meta:
        model = Game
        fields = ['id', 'match', 'home_player', 'away_player',
                  'winner', 'home_score', 'away_score']
        read_only_fields = ['id']


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for the Match model."""
    match_night = serializers.PrimaryKeyRelatedField(
        queryset=MatchNight.objects.all())
    match_time = serializers.TimeField(required=False)

    class Meta:
        model = Match
        fields = [
            'id', 'match_night', 'home_team', 'away_team', 'match_time',
            'home_score', 'away_score', 'status', 'home_race_to',
            'away_race_to', 'team_snapshot'
        ]
        read_only_fields = ['id']


class MatchNightSerializer(serializers.ModelSerializer):
    """Serializer for the MatchNight model."""
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = MatchNight
        fields = ['id', 'date', 'start_time', 'status', 'matches']
        read_only_fields = ['id']


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for the Schedule model."""
    matchnights = MatchNightSerializer(many=True, read_only=True)
    default_start_time = serializers.TimeField(
        format='%H:%M:%S', required=False)
    start_date = serializers.DateField(required=True)
    num_weeks = serializers.IntegerField(required=True)

    class Meta:
        model = Schedule
        fields = ['id', 'start_date',
                  'num_weeks', 'default_start_time', 'matchnights']
        read_only_fields = ['id']

    def validate(self, data):
        """Ensure only one schedule exists per season."""
        season = data.get('season')
        if Schedule.objects.filter(season=season).exists():
            raise serializers.ValidationError("A schedule already exists for this season.")
        return data


class SeasonSerializer(serializers.ModelSerializer):
    """Serializer for the Season model."""
    schedule = serializers.SerializerMethodField()
    teamseason = TeamSeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ['id', 'name', 'year', 'is_active',
                  'league', 'schedule', 'teamseason']
        read_only_fields = ['id', 'league']

    def get_schedule(self, obj):
        """Return the associated schedule or None if it doesn't exist."""
        schedule = getattr(obj, 'schedule', None)
        if schedule:
            return ScheduleSerializer(schedule).data
        return None


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for the League model."""
    admin = serializers.StringRelatedField(read_only=True)
    additional_admins = serializers.StringRelatedField(
        many=True, read_only=True)
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = League
        fields = ['id', 'name', 'is_active',
                  'admin', 'additional_admins', 'seasons']
