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

        # Return leagues where the user is an admin or part of the league
        return League.objects.filter(
            models.Q(admin=user) |
            models.Q(additional_admins=user) |
            models.Q(teams__players__user=user)
        ).distinct()

    def perform_authentication(self, request):
        super().perform_authentication(request)

    def perform_create(self, serializer):
        """Create a new league."""
        serializer.save(admin=self.request.user)
