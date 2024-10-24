"""
Tests team season API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Team,
    League,
    Player,
    Season,
    # TeamPlayer,
    TeamSeason,
)
# from league.serializers import TeamSeasonSerializer


def team_seasons_url(league_id, season_id, team_season_id):
    """Return the team season list URL."""
    return reverse(
        'league:teamseason-detail',
        args=[league_id, season_id, team_season_id]
    )


def team_seasons_list_url(league_id, season_id):
    """Return the team season detail URL."""
    return reverse(
        'league:teamseason-list',
        args=[league_id, season_id]
    )


def create_league(admin_user, **params):
    """Create and return a sample league"""
    defaults = {
        'name': 'Sample League',
        'is_active': True,
    }
    defaults.update(params)

    return League.objects.create(admin=admin_user, **defaults)


def create_season(league, **params):
    """Create and return a sample season"""
    defaults = {
        'name': 'Sample Season',
        'year': 2024,
        'league': league,
    }
    defaults.update(params)

    return Season.objects.create(**defaults)


def create_team(league, **params):
    """Create and return a sample team"""
    defaults = {
        'name': 'Sample Team',
        'league': league,
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_player(**params):
    """Create and return a sample player"""
    defaults = {
        'name': 'Sample Player',
    }
    defaults.update(params)

    return Player.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Create and return a sample team season"""
    defaults = {
        'team': team,
        'season': season,
        'captain': create_player(),
    }
    defaults.update(params)

    return TeamSeason.objects.create(**defaults)


class PublicTeamSeasonApiTests(TestCase):
    """Test the publicly available team season API"""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(
            admin_user=get_user_model().objects.create_user(
                'admin2@admin123@.com',
                'testpass',
                is_admin=True,
            )
        )
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.team_season = create_team_season(self.team, self.season)

    def test_login_required(self):
        """Test that login is required for retrieving team seasons"""
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
