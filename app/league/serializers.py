from rest_framework import serializers
from core.models import League  # Assuming your model is named League
from core.models import Team  # Assuming League is related to Team

# class TeamSerializer(serializers.ModelSerializer):
#     """Serializer for teams associated with the league"""
#     class Meta:
#         model = Team
#         fields = ['id', 'name', 'players']  # Customize this based on your Team model


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for the League model"""
    # teams = TeamSerializer(many=True, read_only=True)  # Nested serializer for teams
    admin = serializers.StringRelatedField(read_only=True)  # Assuming admin is a User model
    additional_admins = serializers.StringRelatedField(many=True, read_only=True)  # Assuming multiple admins

    class Meta:
        model = League
        fields = ['id', 'name', 'season', 'is_active', 'year', 'admin', 'additional_admins']  # Add 'teams' later

    def create(self, validated_data):
        """Create a new league"""
        # Admin will be set during the view's perform_create method, so we don't need it here
        return super().create(validated_data)
