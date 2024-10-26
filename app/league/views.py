from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from core.models import (
    League,
    Season,
    Schedule,
    MatchNight,
    Match,
    Game,
    TeamSeason,
    Team,
    Player
)
from league import serializers
from team.serializers import TeamSeasonSerializer
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


class ScheduleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_schedule(self, season_id):
        """Retrieve the schedule for the given season_id."""
        return Schedule.objects.filter(season_id=season_id).first()

    def create(self, request, league_id=None, season_id=None):
        season = Season.objects.get(id=season_id)
        serializer = serializers.ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(season=season)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, league_id=None, season_id=None):
        schedule = self.get_schedule(season_id)
        if not schedule:
            return Response(
                {"detail": "Schedule not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = serializers.ScheduleSerializer(schedule)
        return Response(serializer.data)

    def update(self, request, league_id=None, season_id=None, partial=False):
        schedule = self.get_schedule(season_id)
        if not schedule:
            return Response(
                {"detail": "Schedule not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = serializers.ScheduleSerializer(
            schedule, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, league_id=None, season_id=None):
        return self.update(request, league_id, season_id, partial=True)

    def destroy(self, request, league_id=None, season_id=None):
        schedule = self.get_schedule(season_id)
        if not schedule:
            return Response(
                {"detail": "Schedule not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SeasonViewSet(viewsets.ModelViewSet):
    """View for managing season APIs."""
    serializer_class = serializers.SeasonSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Return all seasons for the given league with optimized query."""
        league_id = self.kwargs.get('league_id')
        return Season.objects.filter(
            league_id=league_id
        ).prefetch_related('teamseason__team_players')

    def perform_create(self, serializer):
        """Create a new season and associate it with the league."""
        league_id = self.kwargs['league_id']
        league = get_object_or_404(League, id=league_id)
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


class TeamSeasonViewSet(viewsets.ModelViewSet):
    """View for managing TeamSeason API requests."""
    queryset = TeamSeason.objects.all()
    serializer_class = TeamSeasonSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsAdminOrLeagueMember]

    def get_queryset(self):
        """Filter and optimize queryset for TeamSeason."""
        queryset = self.queryset.prefetch_related('team_players')

        team_id = self.request.query_params.get('team_id')
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        season_id = self.request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(season_id=season_id)

        return queryset

    def post(self, request, *args, **kwargs):
        """Handle POST requests explicitly."""
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Handle POST requests for TeamSeason creation."""
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Create a new team season instance."""
        team_id = self.request.data.get('team')
        season_id = self.request.data.get('season')

        try:
            team = Team.objects.get(id=team_id)
            season = Season.objects.get(id=season_id)
        except (Team.DoesNotExist, Season.DoesNotExist) as e:
            raise ValidationError(f"Invalid team or season: {str(e)}")

        # Default values for the new TeamSeason
        serializer.save(team=team, season=season, name=team.name,
                        wins=0, losses=0, games_won=0, games_lost=0)

    def perform_update(self, serializer):
        """Update a team season instance."""
        captain_id = self.request.data.get('captain')
        try:
            captain = Player.objects.get(id=captain_id)
            serializer.save(captain=captain)
        except Player.DoesNotExist:
            raise ValidationError(
                f"Invalid captain: \
                    Player with ID {captain_id} does not exist.")
