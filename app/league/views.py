from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import models

from core.models import League, Season, Schedule
from league import serializers
from .permissions import IsAdminOrLeagueMember


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing schedule CRUD operations."""
    serializer_class = serializers.ScheduleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return the schedules for the given season."""
        season_id = self.kwargs['season_id']
        return Schedule.objects.filter(season_id=season_id)

    def perform_create(self, serializer):
        """Create a new schedule for the given season."""
        season_id = self.kwargs['season_id']
        serializer.save(season_id=season_id)

    def get_object(self):
        """Retrieve and return a schedule,
        and ensure league permissions are checked."""
        obj = super().get_object()
        league = obj.season.league
        self.check_object_permissions(self.request, league)
        return obj


class SeasonViewSet(viewsets.ModelViewSet):
    """View for managing season APIs."""
    serializer_class = serializers.SeasonSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return seasons for the league that the
        current authenticated user is associated with."""
        user = self.request.user
        league_id = self.kwargs.get('league_id')

        seasons = Season.objects.filter(
            models.Q(league__admin=user) |
            models.Q(league__additional_admins=user),
            league_id=league_id
        )

        seasons_as_player = Season.objects.filter(
            league__seasons__teamseason__players__user=user,
            league_id=league_id
        )

        return (seasons | seasons_as_player).distinct()

    def perform_create(self, serializer):
        """Create a new season."""
        league_id = self.kwargs['league_id']
        league = League.objects.get(id=league_id)
        serializer.save(league=league)


class LeagueViewSet(viewsets.ModelViewSet):
    """View for managing league APIs"""
    serializer_class = serializers.LeagueSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return leagues the current authenticated user is associated with."""
        user = self.request.user

        leagues = League.objects.filter(
            models.Q(admin=user) |
            models.Q(additional_admins=user)
        )

        leagues_as_player = League.objects.filter(
            seasons__teamseason__players__user=user
        )

        return (leagues | leagues_as_player).distinct()

    def perform_authentication(self, request):
        super().perform_authentication(request)

    def perform_create(self, serializer):
        """Create a new league."""
        serializer.save(admin=self.request.user)
