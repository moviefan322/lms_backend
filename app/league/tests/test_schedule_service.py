from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date
from core.models import (
    Schedule,
    MatchNight,
    Match,
    League,
    Season,
    TeamSeason
)
from league.services import ScheduleService
from django.contrib.auth import get_user_model
from .test_helpers import (
    create_league,
    create_season,
    create_team,
    create_team_season
)

from core.tests.test_models import create_admin, random_string


def create_league(admin_user, **params):
    """Helper function to create a league."""
    defaults = {'name': random_string(), 'is_active': True}
    defaults.update(params)
    return League.objects.create(admin=admin_user, **defaults)


def create_season(league, **params):
    """Helper function to create a season."""
    defaults = {'name': random_string(), 'year': 2024}
    defaults.update(params)
    return Season.objects.create(league=league, **defaults)


def create_team_season(season, **params):
    """Helper function to create a team season."""
    defaults = {'name': random_string()}
    defaults.update(params)
    return TeamSeason.objects.create(season=season, **defaults)


def schedule_url(league_id, season_id):
    """Helper function to get the schedule URL."""
    return reverse('league:schedule-list', args=[league_id, season_id])


def generate_schedule_url(schedule_id):
    """Helper function to get the generate schedule URL."""
    return reverse('league:generate-schedule', args=[schedule_id])


class ScheduleServiceTests(TestCase):
    def setUp(self):
        """Set up basic data for testing."""
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)
        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date='2024-10-01',
            num_weeks=8  # Assuming 8 weeks for 16 teams, adjust as needed
        )
        # Create 16 teams
        self.teams = []
        for i in range(16):
            team = create_team_season(create_team(self.league), self.season)
            self.teams.append(team)

    def test_balances_home_and_away_games(self):
        """Test that the schedule balances home and away games."""
        service = ScheduleService(self.schedule)
        service.generate_schedule()

        home_away_tracker = {
            team.id: {'home': 0, 'away': 0} for team in self.teams
        }

        # Tally home and away games
        match_nights = MatchNight.objects.filter(schedule=self.schedule)
        for night in match_nights:
            matches = Match.objects.filter(match_night=night)
            for match in matches:
                home_away_tracker[match.home_team.id]['home'] += 1
                home_away_tracker[match.away_team.id]['away'] += 1

        # Ensure home/away balance per team
        for team_id, counts in home_away_tracker.items():
            self.assertTrue(abs(counts['home'] - counts['away']) <= 3,
                            f"Team {team_id} has\
                                unbalanced home/away: {counts}")

    def test_all_teams_have_num_weeks_matches(self):
        """Test that each team has the correct number of scheduled matches."""
        service = ScheduleService(self.schedule)
        service.generate_schedule()

        team_match_count = {team.id: 0 for team in self.teams}

        # Count matches per team
        match_nights = MatchNight.objects.filter(schedule=self.schedule)
        for night in match_nights:
            matches = Match.objects.filter(match_night=night)
            for match in matches:
                team_match_count[match.home_team.id] += 1
                team_match_count[match.away_team.id] += 1

        # Ensure each team has the correct number of matches
        for team_id, count in team_match_count.items():
            self.assertEqual(count, self.schedule.num_weeks,
                             f"Team {team_id} has {count} matches\
                                instead of {self.schedule.num_weeks}")


class ScheduleApiTests(TestCase):
    """Tests for the Schedule API."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)
        self.league = create_league(self.admin_user)
        self.season = create_season(self.league)

    def test_create_schedule(self):
        """Test creating a schedule."""
        payload = {
            'start_date': date(2024, 10, 1),
            'num_weeks': 4,
            'default_start_time': '19:00'
        }
        url = schedule_url(self.league.id, self.season.id)
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_date', response.data)
        self.assertEqual(response.data['start_date'], '2024-10-01')

    def test_generate_schedule(self):
        """Test generating a schedule."""
        # First, create the schedule
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        # Create teams for the schedule
        team1 = create_team_season(season=self.season, name="Team 1")
        team2 = create_team_season(season=self.season, name="Team 2")

        url = generate_schedule_url(schedule.id)
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('matchnights', response.data)
        self.assertGreater(len(response.data['matchnights']), 0)

        # Additional assertions can check that match nights and matches were created as expected

    def test_retrieve_schedule(self):
        """Test retrieving a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', response.data)
        self.assertEqual(response.data['start_date'], '2024-10-01')
