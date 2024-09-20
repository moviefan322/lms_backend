from rest_framework import serializers
from core.models import League  # import Team


# class TeamSerializer(serializers.ModelSerializer):
#     """Serializer for teams associated with the league"""
#     class Meta:
#         model = Team
#         fields = ['id', 'name', 'players']


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for the League model"""
    # teams = TeamSerializer(many=True, read_only=True)
    admin = serializers.StringRelatedField(
        read_only=True)  # Assuming admin is a User model
    additional_admins = serializers.StringRelatedField(
        many=True, read_only=True)  # Assuming multiple admins

    class Meta:
        model = League
        fields = [
            'id', 'name', 'season', 'is_active',
            'year', 'admin', 'additional_admins'
        ]  # Add 'teams' later
