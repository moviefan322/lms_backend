from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import models

from core.models import (
    League,
    Season,
    Schedule,
    MatchNight,
    Match,
    Game
)
from league import serializers
from .permissions import IsAdminOrLeagueMember


class GameViewSet(viewsets.ModelViewSet):
    """ViewSet for managing game CRUD operations."""
    serializer_class = serializers.GameSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return games for the given season."""
        season_id = self.kwargs['season_id']
        return Game.objects.filter(
            match__match_night__schedule__season_id=season_id
        )

    def perform_create(self, serializer):
        """Create a new game for the given season."""
        serializer.save()

    def get_object(self):
        """Retrieve and return a game,
        ensuring league permissions are checked."""
        obj = super().get_object()

        league = obj.match.match_night.schedule.season.league
        self.check_object_permissions(self.request, league)

        return obj


class MatchViewSet(viewsets.ModelViewSet):
    """ViewSet for managing match CRUD operations."""
    serializer_class = serializers.MatchSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return matches for the given season."""
        season_id = self.kwargs['season_id']
        return Match.objects.filter(match_night__schedule__season_id=season_id)

    def get_object(self):
        """Retrieve and return a match,
        and ensure league permissions are checked."""
        obj = super().get_object()
        league = obj.match_night.schedule.season.league
        self.check_object_permissions(self.request, league)
        return obj


class MatchNightViewSet(viewsets.ModelViewSet):
    """ViewSet for managing match nights."""
    serializer_class = serializers.MatchNightSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return match nights for the given season."""
        schedule_id = self.kwargs['schedule_id']
        return MatchNight.objects.filter(schedule_id=schedule_id)

    def perform_create(self, serializer):
        """Create a new match night for the given schedule."""
        schedule_id = self.kwargs['schedule_id']
        schedule = Schedule.objects.get(id=schedule_id)
        serializer.save(schedule=schedule)

    def perform_update(self, serializer):
        """Update a match night."""
        schedule_id = self.kwargs['schedule_id']
        schedule = Schedule.objects.get(id=schedule_id)
        serializer.save(schedule=schedule)

    def get_object(self):
        """Retrieve and return a match night,
        and ensure league permissions are checked."""
        obj = super().get_object()
        league = obj.schedule.season.league
        self.check_object_permissions(self.request, league)
        return obj


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
        user = self.request.user

        if user.is_admin:
            admin_leagues = League.objects.filter(admin=user)
            additional_admin_leagues = League.objects.filter(
                additional_admins=user)

            leagues = admin_leagues | additional_admin_leagues
            return leagues.distinct()

        player_leagues = League.objects.filter(
            seasons__teamseason__players=user.player_profile
        ).distinct()

        return player_leagues

    def perform_authentication(self, request):
        super().perform_authentication(request)

    def perform_create(self, serializer):
        """Create a new league."""
        serializer.save(admin=self.request.user)
