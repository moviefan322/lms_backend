from rest_framework import serializers
from core.models import League, Season, Schedule, MatchNight, Match


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for the Match model."""
    match_night = serializers.PrimaryKeyRelatedField(queryset=MatchNight.objects.all())
    match_time = serializers.TimeField(required=False)

    class Meta:
        model = Match
        fields = [
            'id', 'match_night', 'home_team', 'away_team', 'match_time',
            'home_score', 'away_score', 'status', 'home_race_to', 'away_race_to',
            'team_snapshot'
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

    class Meta:
        model = Schedule
        fields = ['id', 'start_date',
                  'num_weeks', 'default_start_time', 'matchnights']
        read_only_fields = ['id']


class SeasonSerializer(serializers.ModelSerializer):
    """Serializer for the Season model."""

    class Meta:
        model = Season
        fields = ['id', 'name', 'year', 'is_active', 'league']
        read_only_fields = ['id', 'league']


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
