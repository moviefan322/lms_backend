from rest_framework import serializers
from core.models import League, Season, Schedule, MatchNight


class MatchNightSerializer(serializers.ModelSerializer):
    """Serializer for the MatchNight model."""

    class Meta:
        model = MatchNight
        fields = ['id', 'date', 'start_time', 'status']
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
