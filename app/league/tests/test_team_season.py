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
    TeamPlayer,
    TeamSeason,
)
from league.serializers import TeamSeasonSerializer


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


def create_team_player(team_season, player, **params):
    """Create and return a sample team player"""
    defaults = {
        'team_season': team_season,
        'player': player,
    }
    defaults.update(params)

    return TeamPlayer.objects.create(**defaults)


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


class AdminTeamSeasonApiTests(TestCase):
    """Test the team season API for admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@admin123@.com',
            'testpass',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)
        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.new_team = create_team(league=self.league)
        self.player = create_player()
        self.newPlayer = create_player()
        self.team_season = create_team_season(self.team, self.season, captain=self.player)

    def test_retrieve_team_seasons(self):
        """Test retrieving a list of team seasons"""
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_view_team_season_detail(self):
        """Test viewing a team season detail"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_team_season(self):
        """Test creating a new team season"""
        payload = {
            'team': self.new_team.id,
            'season': self.season.id,
            'captain': self.newPlayer.id,
        }
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['team'], payload['team'])
        self.assertEqual(res.data['season'], payload['season'])
        self.assertEqual(res.data['captain'], payload['captain'])

    def test_partial_update_team_season(self):
        """Test updating a team season with patch"""
        payload = {'captain': self.newPlayer.id}
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.patch(url, payload)

        self.team_season.refresh_from_db()
        self.assertEqual(self.newPlayer.id, payload['captain'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update_team(self):
        """Test updating a team season with put"""
        team = create_team(self.league, name='New Team Name')
        payload = {
            'team': team.id,
            'season': self.season.id,
            'captain': self.newPlayer.id,
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.put(url, payload)

        self.team_season.refresh_from_db()
        self.assertEqual(self.team_season.team.id, payload['team'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_team_season(self):
        """Test deleting a team season"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamSeason.objects.filter(id=self.team_season.id).exists())

    def test_invalid_team_season(self):
        """Test creating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_season_update(self):
        """Test updating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_team_season_partial_update(self):
        """Test updating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_season_delete(self):
        """Test deleting a team season with invalid payload"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamSeason.objects.filter(id=self.team_season.id).exists())


class AdditionalAdminTeamSeasonApiTests(TestCase):
    """Test the team season API for additional admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@admin123@.com',
            'testpass',
            is_admin=True,
        )
        self.additional_admin_user = get_user_model().objects.create_user(
            'admin2@admin123@.com',
            'testpass',
            is_admin=True,
        )
        self.client.force_authenticate(self.additional_admin_user)
        self.league = create_league(admin_user=self.admin_user)
        self.league.additional_admins.add(self.additional_admin_user)
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.new_team = create_team(league=self.league)
        self.player = create_player()
        self.newPlayer = create_player()
        self.team_season = create_team_season(self.team, self.season, captain=self.player)

    def test_retrieve_team_seasons(self):
        """Test retrieving a list of team seasons"""
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_view_team_season_detail(self):
        """Test viewing a team season detail"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_team_season(self):
        """Test creating a new team season"""
        payload = {
            'team': self.new_team.id,
            'season': self.season.id,
            'captain': self.newPlayer.id,
        }
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['team'], payload['team'])
        self.assertEqual(res.data['season'], payload['season'])
        self.assertEqual(res.data['captain'], payload['captain'])

    def test_partial_update_team_season(self):
        """Test updating a team season with patch"""
        payload = {'captain': self.newPlayer.id}
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )

        res = self.client.patch(url, payload)

        self.team_season.refresh_from_db()
        self.assertEqual(self.newPlayer.id, payload['captain'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update_team(self):
        """Test updating a team season with put"""
        team = create_team(self.league, name='New Team Name')
        payload = {
            'team': team.id,
            'season': self.season.id,
            'captain': self.newPlayer.id,
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.put(url, payload)

        self.team_season.refresh_from_db()
        self.assertEqual(self.team_season.team.id, payload['team'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_team_season(self):
        """Test deleting a team season"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamSeason.objects.filter(id=self.team_season.id).exists())

    def test_invalid_team_season(self):
        """Test creating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_season_update(self):
        """Test updating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_season_partial_update(self):
        """Test updating a team season with invalid payload"""
        payload = {
            'team': '',
            'season': '',
            'captain': '',
        }
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_team_season_delete(self):
        """Test deleting a team season with invalid payload"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamSeason.objects.filter(id=self.team_season.id).exists())


class PlayerTeamSeasonApiTests(TestCase):
    """Test the team season API for player users"""

    def setUp(self):
        self.client = APIClient()
        self.player_user = get_user_model().objects.create_user(
            'player@player123@.com',
            'testpass',
            is_admin=False,
        )
        self.client.force_authenticate(self.player_user)
        self.league = create_league(
            admin_user=get_user_model().objects.create_user(
                'admin@admin123@.com',
                'testpass',
                is_admin=True,
            )
        )
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.new_team = create_team(league=self.league)
        self.player = create_player()
        self.player_user.player_profile = self.player
        self.newPlayer = create_player()
        self.team_season = create_team_season(self.team, self.season, captain=self.player)
        self.team_player = create_team_player(self.team_season, self.player)

    def test_retrieve_team_seasons(self):
        """Test retrieving a list of team seasons"""
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_view_team_season_detail(self):
        """Test viewing a team season detail"""
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_create_team_season(self):
        """Test creating a new team season"""
        payload = {
            'team': self.new_team.id,
            'season': self.season.id,
            'captain': self.newPlayer.id,
        }
        url = team_seasons_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_team_season(self):
        """Test updating a team season with patch"""
        payload = {'captain': self.newPlayer.id}
        url = team_seasons_url(
            self.league.id,
            self.season.id,
            self.team_season.id
        )
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
