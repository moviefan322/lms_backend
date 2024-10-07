from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Schedule, MatchNight, Match
from league.services import ScheduleService
from django.contrib.auth import get_user_model
from .test_helpers import (
    create_league,
    create_season,
    create_team,
    create_team_season
)


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
        self.league = create_league()
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date='2024-10-01',
            num_weeks=4
        )
        # Create teams
        self.team_season1 = create_team_season(
            create_team(self.league), self.season)
        self.team_season2 = create_team_season(
            create_team(self.league), self.season)
        self.team_season3 = create_team_season(
            create_team(self.league), self.season)
        self.team_season4 = create_team_season(
            create_team(self.league), self.season)
        self.teams = [self.team_season1, self.team_season2,
                      self.team_season3, self.team_season4]

    def test_balances_home_and_away_games(self):
        """Test that the schedule balances home and away games."""
        service = ScheduleService(self.schedule)
        service.generate_schedule()

        home_away_tracker = {team.id: {'home': 0, 'away': 0}
                             for team in self.teams}

        # Tally home and away games
        match_nights = MatchNight.objects.filter(schedule=self.schedule)
        for night in match_nights:
            matches = Match.objects.filter(match_night=night)
            for match in matches:
                home_away_tracker[match.home_team.id]['home'] += 1
                home_away_tracker[match.away_team.id]['away'] += 1

        # Ensure home/away balance per team
        for team_id, counts in home_away_tracker.items():
            self.assertTrue(abs(counts['home'] - counts['away']) <= 1,
                            f"Team {team_id} has unbalanced \
                                home/away: {counts}")

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
                             f"Team {team_id} has {count} matches \
                                instead of {self.schedule.num_weeks}")
