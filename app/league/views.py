from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import models

from core.models import League
from league import serializers
from .permissions import IsAdminOrReadOnly


class LeagueViewSet(viewsets.ModelViewSet):
    """View for managing league APIs"""
    serializer_class = serializers.LeagueSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Return leagues the current authenticated user is associated with."""
        user = self.request.user

        # Check if the user is an admin or in the additional admins of the league
        leagues = League.objects.filter(
            models.Q(admin=user) |
            models.Q(additional_admins=user)
        )

        # Check if the user is a player in any team in the league's seasons
        leagues_as_player = League.objects.filter(
            seasons__teamseason__players__user=user
        )

        return (leagues | leagues_as_player).distinct()

    def perform_authentication(self, request):
        super().perform_authentication(request)

    def perform_create(self, serializer):
        """Create a new league."""
        serializer.save(admin=self.request.user)
