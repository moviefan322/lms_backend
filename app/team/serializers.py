from rest_framework import serializers
from core.models import Team


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for teams associated with the league"""
    class Meta:
        model = Team
        fields = ['id', 'league', 'name', 'captain']  # add players
