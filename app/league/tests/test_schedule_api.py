from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import (
    Schedule,
    MatchNight,
    Match,
    Game
)
from core.tests.test_models import create_admin
from .test_helpers import (
    create_league,
    create_season,
    create_team,
    create_team_season,
    create_player,
    create_team_player
)
from django.contrib.auth import get_user_model
from datetime import date, time


def schedule_url(league_id, season_id):
    """Return the schedule URL for a given league and season."""
    return reverse('league:season-schedule', args=[league_id, season_id])


def matches_list_url(league_id, season_id):
    """Return the match list URL for a given league and season."""
    return reverse('league:match-list', args=[league_id, season_id])


def games_list_url(league_id, season_id):
    """Return the game list URL for a given league and season."""
    return reverse('league:game-list', args=[league_id, season_id])


def matchnight_url(league_id, schedule_id):
    """Return the match night list URL for a given league and schedule."""
    return reverse('league:matchnight-list', args=[league_id, schedule_id])


def matchnight_detail_url(league_id, schedule_id, matchnight_id):
    """Return the match night detail URL for a given league and schedule."""
    return reverse('league:matchnight-detail', args=[
        league_id, schedule_id, matchnight_id
    ])


def match_detail_url(league_id, season_id, match_id):
    """Return the match URL for a given league, season, and match."""
    return reverse('league:match-detail', args=[
        league_id, season_id, match_id
    ])


def game_detail_url(league_id, season_id, game_id):
    """Return the game URL for a given league, season, and game."""
    return reverse('league:game-detail', args=[
        league_id, season_id, game_id
    ])


def create_matchnight(**params):
    """Helper function to create a match night."""
    defaults = {
        'date': date(2024, 10, 1),
        'start_time': '19:00'
    }
    defaults.update(params)
    return MatchNight.objects.create(**defaults)


def create_match(match_night, home_team, away_team):
    """Helper function to create a match."""
    return Match.objects.create(
        match_night=match_night,
        home_team=home_team,
        away_team=away_team
    )


def create_game(match, home_player, away_player):
    """Helper function to create a game."""
    return Game.objects.create(
        match=match,
        home_player=home_player,
        away_player=away_player
    )


class PublicMatchNightApiTests(TestCase):
    """Test match night access for unauthenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(admin_user=create_admin())
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

    def test_unauthenticated_user_cannot_create_matchnight(self):
        """Test that an unauthenticated user cannot create a match night."""
        payload = {
            'date': date(2024, 10, 1),
            'start_time': '19:00'
        }

        res = self.client.post(matchnight_url(
            self.league.id, self.schedule.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_matchnight(self):
        """Test that an unauthenticated user cannot view a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_modify_matchnight(self):
        """Test that an unauthenticated user cannot modify a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        payload = {'start_time': '20:00'}

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_matchnight(self):
        """Test that an unauthenticated user cannot delete a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicMatchApiTests(TestCase):
    """Test match access for unauthenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(admin_user=create_admin())
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

    def test_unauthenticated_user_cannot_create_match(self):
        """Test that an unauthenticated user cannot create a match."""
        payload = {
            'match_night': self.matchnight.id,
            'home_team': self.team_season1.id,
            'away_team': self.team_season2.id
        }

        res = self.client.post(matches_list_url(
            self.league.id, self.season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_match(self):
        """Test that an unauthenticated user cannot view a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_modify_match(self):
        """Test that an unauthenticated user cannot modify a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        payload = {'home_team': self.team_season3.id}

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_match(self):
        """Test that an unauthenticated user cannot delete a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicScheduleApiTests(TestCase):
    """Test schedule access for unauthenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(admin_user=create_admin())
        self.season = create_season(league=self.league)

    def test_unauthenticated_user_cannot_create_schedule(self):
        """Test that an unauthenticated user cannot create a schedule."""

        payload = {
            'season': self.season.id,
            'start_date': date(2024, 10, 1),
            'num_weeks': 4,
            'default_start_time': '19:00'
        }

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_schedule(self):
        """Test that an unauthenticated user cannot view a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_modify_schedule(self):
        """Test that an unauthenticated user cannot modify a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_schedule(self):
        """Test that an unauthenticated user cannot delete a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicGameApiTests(TestCase):
    """Test game access for unauthenticated users."""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(admin_user=create_admin())
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.player1 = create_player()
        self.player2 = create_player()
        self.player3 = create_player()
        self.team_player1 = create_team_player(self.team_season1, self.player1)
        self.team_player2 = create_team_player(self.team_season2, self.player2)
        self.team_player3 = create_team_player(self.team_season3, self.player3)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )
        self.match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        self.game = create_game(
            match=self.match,
            home_player=self.team_player1,
            away_player=self.team_player2
        )

    def test_unauthenticated_user_cannot_create_game(self):
        """Test that an unauthenticated user cannot create a game."""
        payload = {
            'match': self.match.id,
            'home_player': self.team_player1.id,
            'away_player': self.team_player2.id
        }

        url = games_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_view_game(self):
        """Test that an unauthenticated user cannot view a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_modify_game(self):
        """Test that an unauthenticated user cannot modify a game."""
        payload = {'home_score': 10}

        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_user_cannot_delete_game(self):
        """Test that an unauthenticated user cannot delete a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminScheduleApiTests(TestCase):
    """Test schedule access for admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)

    def test_admin_can_create_schedule(self):
        """Test that an admin user can create a schedule."""
        payload = {
            'season': self.season.id,
            'start_date': date(2024, 10, 1),
            'num_weeks': 4,
            'default_start_time': '19:00'
        }

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_admin_can_view_schedule(self):
        """Test that an admin user can view a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_admin_can_modify_schedule(self):
        """Test that an admin user can modify a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['num_weeks'], 6)

    def test_admin_can_delete_schedule(self):
        """Test that an admin user can delete a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdminMatchNightApiTests(TestCase):
    """Test match night access for admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

    def test_admin_can_create_matchnight(self):
        """Test that an admin user can create a match night."""
        payload = {
            'schedule': self.schedule.id,
            'date': date(2024, 10, 1),
            'start_time': '19:00'
        }

        res = self.client.post(matchnight_url(
            self.league.id, self.schedule.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('date', res.data)
        self.assertEqual(res.data['date'], '2024-10-01')

    def test_match_night_inherits_start_time_from_schedule(self):
        """Test that a match night inherits the
        start time from the schedule."""
        payload = {
            'schedule': self.schedule.id,
            'date': date(2024, 10, 1)
        }

        res = self.client.post(matchnight_url(
            self.league.id, self.schedule.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_time', res.data)
        self.assertEqual(res.data['start_time'], '19:00:00')

    def test_admin_can_view_matchnight(self):
        """Test that an admin user can view a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('date', res.data)
        self.assertEqual(res.data['date'], '2024-10-01')

    def test_admin_can_modify_matchnight(self):
        """Test that an admin user can modify a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        payload = {'start_time': '20:00'}

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['start_time'], '20:00:00')

    def test_partial_update_matchnight(self):
        """Test updating a match night with a PATCH request."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time=time(19, 0)
        )

        payload = {'start_time': '20:00'}

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        self.client.patch(url, payload)

        matchnight.refresh_from_db()
        self.assertEqual(matchnight.start_time, time(20, 0))

    def test_admin_can_delete_matchnight(self):
        """Test that an admin user can delete a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdminMatchApiTests(TestCase):
    """Test match access for admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

    def test_admin_can_create_match(self):
        """Test that an admin user can create a match."""
        payload = {
            'match_night': self.matchnight.id,
            'home_team': self.team_season1.id,
            'away_team': self.team_season2.id
        }

        res = self.client.post(matches_list_url(
            self.league.id, self.season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('home_team', res.data)
        self.assertEqual(res.data['home_team'], self.team_season1.id)

    def test_admin_can_view_all_matches(self):
        """Test that an admin user can view all matches."""
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season2,
            away_team=self.team_season3
        )

        res = self.client.get(matches_list_url(self.league.id, self.season.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_admin_can_view_match(self):
        """Test that an admin user can view a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('home_team', res.data)
        self.assertEqual(res.data['home_team'], self.team_season1.id)

    def test_admin_can_modify_match(self):
        """Test that an admin user can modify a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        payload = {'home_team': self.team_season3.id}

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['home_team'], self.team_season3.id)

    def test_admin_can_delete_match(self):
        """Test that an admin user can delete a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdminGameApiTests(TestCase):
    """Test game access for admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.player1 = create_player()
        self.player2 = create_player()
        self.player3 = create_player()
        self.team_player1 = create_team_player(self.team_season1, self.player1)
        self.team_player2 = create_team_player(self.team_season2, self.player2)
        self.team_player3 = create_team_player(self.team_season3, self.player3)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )
        self.match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        self.game = create_game(
            match=self.match,
            home_player=self.team_player1,
            away_player=self.team_player2
        )

    def test_admin_can_create_game(self):
        """Test that an admin user can create a game."""
        payload = {
            'match': self.match.id,
            'home_player': self.team_player1.id,
            'away_player': self.team_player2.id
        }

        url = games_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('home_player', res.data)
        self.assertEqual(res.data['home_player'], self.team_player1.id)

    def test_admin_can_view_game(self):
        """Test that an admin user can view a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('home_player', res.data)
        self.assertEqual(res.data['home_player'], self.team_player1.id)

    def test_admin_can_modify_game(self):
        """Test that an admin user can modify a game."""
        payload = {'home_score': 10}

        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['home_score'], 10)

    def test_admin_can_delete_game(self):
        """Test that an admin user can delete a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def other_admin_cannot_modify_game(self):
        """Test that an admin user cannot modify another admin's game."""
        other_admin = create_admin()
        self.client.force_authenticate(other_admin)

        payload = {'home_score': 10}

        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def other_admin_cannot_delete_game(self):
        """Test that an admin user cannot delete another admin's game."""
        other_admin = create_admin()
        self.client.force_authenticate(other_admin)

        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class AdditionalAdminScheduleApiTests(TestCase):
    """Test schedule access for additional admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)

        self.additional_admin = get_user_model().objects.create_user(
            'example@example.com',
            'test123'
        )
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

    def test_additional_admin_can_create_schedule(self):
        """Test that an additional admin user can create a schedule."""
        payload = {
            'season': self.season.id,
            'start_date': date(2024, 10, 1),
            'num_weeks': 4,
            'default_start_time': '19:00'
        }

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_additional_admin_can_view_schedule(self):
        """Test that an additional admin user can view a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_additional_admin_can_modify_schedule(self):
        """Test that an additional admin user can modify a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['num_weeks'], 6)

    def test_additional_admin_can_delete_schedule(self):
        """Test that an additional admin user can delete a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdditionalAdminMatchNightApiTests(TestCase):
    """Test match night access for additional admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        self.additional_admin = get_user_model().objects.create_user(
            'additional_admin@example.com',
            'test123'
        )
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

    def test_additional_admin_can_create_matchnight(self):
        """Test that an additional admin user can create a match night."""
        payload = {
            'date': date(2024, 10, 1),
            'start_time': '19:00'
        }

        res = self.client.post(matchnight_url(
            self.league.id, self.schedule.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('date', res.data)
        self.assertEqual(res.data['date'], '2024-10-01')

    def test_additional_admin_can_view_matchnight(self):
        """Test that an additional admin user can view a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('date', res.data)
        self.assertEqual(res.data['date'], '2024-10-01')

    def test_additional_admin_can_modify_matchnight(self):
        """Test that an additional admin user can modify a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        payload = {'start_time': '20:00'}

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['start_time'], '20:00:00')

    def test_additional_admin_can_delete_matchnight(self):
        """Test that an additional admin user can delete a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdditionalAdminMatchApiTests(TestCase):
    """Test match access for additional admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        self.additional_admin = get_user_model().objects.create_user(
            'additional_admin@example.com',
            'test123',
        )
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

    def test_additional_admin_can_create_match(self):
        """Test that an additional admin user can create a match."""
        payload = {
            'match_night': self.matchnight.id,
            'home_team': self.team_season1.id,
            'away_team': self.team_season2.id
        }

        res = self.client.post(matches_list_url(
            self.league.id, self.season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('home_team', res.data)
        self.assertEqual(res.data['home_team'], self.team_season1.id)

    def test_additional_admin_can_view_all_matches(self):
        """Test that an additional admin user can view all matches."""
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season2,
            away_team=self.team_season3
        )

        res = self.client.get(matches_list_url(self.league.id, self.season.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_additional_admin_can_view_match(self):
        """Test that an additional admin user can view a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('home_team', res.data)
        self.assertEqual(res.data['home_team'], self.team_season1.id)

    def test_additional_admin_can_modify_match(self):
        """Test that an additional admin user can modify a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        payload = {'home_team': self.team_season3.id}

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['home_team'], self.team_season3.id)

    def test_additional_admin_can_delete_match(self):
        """Test that an additional admin user can delete a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class AdditionalAdminGameApiTests(TestCase):
    """Test game access for additional admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=create_player())
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.player1 = create_player()
        self.player2 = create_player()
        self.player3 = create_player()
        self.team_player1 = create_team_player(self.team_season1, self.player1)
        self.team_player2 = create_team_player(self.team_season2, self.player2)
        self.team_player3 = create_team_player(self.team_season3, self.player3)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )
        self.match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        self.game = create_game(
            match=self.match,
            home_player=self.team_player1,
            away_player=self.team_player2
        )

        self.additional_admin = get_user_model().objects.create_user(
            'additional_admin@example.com',
            'test123',
        )
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

    def test_additional_admin_can_create_game(self):
        """Test that an additional admin user can create a game."""
        payload = {
            'match': self.match.id,
            'home_player': self.team_player1.id,
            'away_player': self.team_player2.id
        }

        url = games_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('home_player', res.data)
        self.assertEqual(res.data['home_player'], self.team_player1.id)

    def test_additional_admin_can_view_game(self):
        """Test that an additional admin user can view a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('home_player', res.data)
        self.assertEqual(res.data['home_player'], self.team_player1.id)

    def test_additional_admin_can_modify_game(self):
        """Test that an additional admin user can modify a game."""
        payload = {'home_score': 10}

        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['home_score'], 10)

    def test_additional_admin_can_delete_game(self):
        """Test that an additional admin user can delete a game."""
        url = game_detail_url(self.league.id, self.season.id, self.game.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class UserScheduleApiTests(TestCase):
    """Test schedule access for regular users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)

        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'test123',
        )
        self.client.force_authenticate(self.user)

    def test_user_can_view_schedule(self):
        """Test that a regular user can view a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_user_cannot_modify_schedule(self):
        """Test that a regular user cannot modify a schedule."""
        Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class UserMatchNightApiTests(TestCase):
    """Test match night access for regular users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        self.user = get_user_model().objects.create_user(
            'example@example.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_user_can_view_matchnight(self):
        """Test that a regular user can view a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('date', res.data)
        self.assertEqual(res.data['date'], '2024-10-01')

    def test_user_cannot_modify_matchnight(self):
        """Test that a regular user cannot modify a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        payload = {'start_time': '20:00'}

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_matchnight(self):
        """Test that a regular user cannot delete a match night."""
        matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )

        url = matchnight_detail_url(
            self.league.id, self.schedule.id, matchnight.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class UserMatchApiTests(TestCase):
    """Test match access for regular users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'test123'
        )
        self.player = create_player()
        self.user.player_profile = self.player
        self.user.save()

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=self.player)
        self.team_player = create_team_player(
            team_season=self.team_season1, player=self.player)
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )
        self.client.force_authenticate(self.user)

    def test_user_can_view_match(self):
        """Test that a regular user can view a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('home_team', res.data)
        self.assertEqual(res.data['home_team'], self.team_season1.id)

    def test_user_can_view_all_matches(self):
        """Test that a regular user can view all matches."""
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )
        create_match(
            match_night=self.matchnight,
            home_team=self.team_season2,
            away_team=self.team_season3
        )

        res = self.client.get(matches_list_url(self.league.id, self.season.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_user_cannot_modify_match(self):
        """Test that a regular user cannot modify a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        payload = {'home_team': self.team_season3.id}

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_match(self):
        """Test that a regular user cannot delete a match."""
        match = create_match(
            match_night=self.matchnight,
            home_team=self.team_season1,
            away_team=self.team_season2
        )

        url = match_detail_url(self.league.id, self.season.id, match.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class UserGameApiTests(TestCase):
    """Test game access for regular users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'test123'
        )
        self.player = create_player()
        self.user.player_profile = self.player
        self.user.save()

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team1 = create_team(league=self.league)
        self.team2 = create_team(league=self.league)
        self.team3 = create_team(league=self.league)
        self.team_season1 = create_team_season(
            team=self.team1, season=self.season, captain=self.player)
        self.team_player = create_team_player(
            team_season=self.team_season1, player=self.player)
        self.team_season2 = create_team_season(
            team=self.team2, season=self.season, captain=create_player())
        self.team_season3 = create_team_season(
            team=self.team3, season=self.season, captain=create_player())
        self.player1 = create_player()
        self.player2 = create_player()
        self.player3 = create_player()
        self.team_player1 = create_team_player(self.team_season1, self.player1)
        self.team_player2 = create_team_player(self.team_season2, self.player2)
        self.team_player3 = create_team_player(self.team_season3, self.player3)
        self.schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )
        self.matchnight = create_matchnight(
            schedule=self.schedule,
            date=date(2024, 10, 1),
            start_time='19:00'
        )
        self.client.force_authenticate(self.user)

    def test_user_can_view_game(self):
        """Test that a regular user can view a game."""
        game = create_game(
            match=create_match(
                match_night=self.matchnight,
                home_team=self.team_season1,
                away_team=self.team_season2
            ),
            home_player=self.team_player1,
            away_player=self.team_player2
        )

        url = game_detail_url(self.league.id, self.season.id, game.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['home_player'], self.team_player1.id)

    def test_user_cannot_modify_game(self):
        """Test that a regular user cannot modify a game."""
        game = create_game(
            match=create_match(
                match_night=self.matchnight,
                home_team=self.team_season1,
                away_team=self.team_season2
            ),
            home_player=self.team_player1,
            away_player=self.team_player2
        )

        payload = {'home_score': 10}

        url = game_detail_url(self.league.id, self.season.id, game.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_game(self):
        """Test that a regular user cannot delete a game."""
        game = create_game(
            match=create_match(
                match_night=self.matchnight,
                home_team=self.team_season1,
                away_team=self.team_season2
            ),
            home_player=self.team_player1,
            away_player=self.team_player2
        )

        url = game_detail_url(self.league.id, self.season.id, game.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_create_game(self):
        """Test that a regular user cannot create a game."""
        payload = {
            'match': create_match(
                match_night=self.matchnight,
                home_team=self.team_season1,
                away_team=self.team_season2
            ).id,
            'home_player': self.team_player1.id,
            'away_player': self.team_player2.id
        }

        url = games_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
