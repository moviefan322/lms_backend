from rest_framework import serializers
from core.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for the Player model."""

    class Meta:
        model = Player
        fields = ['id', 'name', 'is_active', 'user']
        read_only_fields = ['id', 'user']


class PlayerDetailSerializer(PlayerSerializer):
    """Serializer for the Player model detail view."""

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = ['id', 'user']