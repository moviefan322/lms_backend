"""
Tests league API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    League,
    Season,
    Team,
    Player,
    TeamSeason,
    TeamPlayer)
from league.serializers import LeagueSerializer
from core.tests.test_models import random_string, create_admin

LEAGUES_URL = reverse('league:league-list')


def detail_url(league_id):
    """Return league detail URL."""
    return reverse('league:league-detail', args=[league_id])


def seasons_url(league_id):
    """Return the season list URL for a given league."""
    return reverse('league:season-list', args=[league_id])


def season_detail_url(league_id, season_id):
    """Return season detail URL for a given league and season."""
    return reverse('league:season-detail', args=[league_id, season_id])


def create_league(admin_user, **params):
    """Helper function to create a league with the provided admin user."""
    defaults = {
        'name': random_string(),
        'is_active': True,
    }
    defaults.update(params)

    return League.objects.create(admin=admin_user, **defaults)


def create_season(league, **params):
    """Helper function to create a season."""
    defaults = {
        'name': random_string(),
        'league': league,
        'year': 2021,
    }
    defaults.update(params)

    return Season.objects.create(**defaults)


def create_team(league, **params):
    """Helper function to create a team."""
    defaults = {
        'name': random_string(),
        'league': league,
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Helper function to create a team season."""
    defaults = {
        'team': team,
        'season': season,
        'captain': create_player(),
    }
    defaults.update(params)

    return TeamSeason.objects.create(**defaults)


def create_player(**params):
    """Helper function to create a player."""
    defaults = {
        'name': random_string(),
    }
    defaults.update(params)

    return Player.objects.create(**defaults)


def create_team_player(team_season, player, **params):
    """Helper function to create a team player."""
    defaults = {
        'team_season': team_season,
        'player': player,
    }
    defaults.update(params)

    return TeamPlayer.objects.create(**defaults)


class PublicLeagueApiTests(TestCase):
    """Test the public access to the league API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_leagues_unauthorized(self):
        """Test retrieving leagues without authentication should fail."""
        res = self.client.get(LEAGUES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_league_detail_unauthorized(self):
        """Test getting league detail without authentication should fail."""
        league = create_league(create_admin())

        url = detail_url(league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_league_unauthorized(self):
        """Test creating a league without authentication should fail."""
        payload = {
            'name': 'Test League',
            'is_active': True,
        }

        res = self.client.post(LEAGUES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminLeagueApiTests(TestCase):
    """Test the authorized admin user league API."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_admin_user = get_user_model().objects.create_user(
            'otheradmin@example.com',
            'test123',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)

    def test_retrieve_leagues(self):
        """Test retrieving leagues."""
        create_league(admin_user=self.admin_user)

        res = self.client.get(LEAGUES_URL)

        leagues = League.objects.all().order_by('id')
        serializer = LeagueSerializer(leagues, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_league_successful(self):
        """Test that an admin user can create a league."""
        payload = {
            'name': 'Test League',
            'is_active': True,
        }
        res = self.client.post(LEAGUES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        league = League.objects.get(id=res.data['id'])
        serializer = LeagueSerializer(league)
        self.assertEqual(res.data, serializer.data)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(league, key))
        self.assertEqual(league.admin, self.admin_user)

    def test_get_league_detail(self):
        """Test retrieving a league's detail."""
        league = create_league(admin_user=self.admin_user)

        url = detail_url(league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = LeagueSerializer(league)
        self.assertEqual(res.data, serializer.data)

    def test_update_league(self):
        """Test updating a league."""
        league = create_league(admin_user=self.admin_user)
        payload = {
            'name': 'Updated League',
            'is_active': False,
        }
        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        league.refresh_from_db()

        serializer = LeagueSerializer(league)
        self.assertEqual(res.data, serializer.data)

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(league, key))
        self.assertEqual(league.admin, self.admin_user)

    def test_admin_cannot_modify_another_admins_league(self):
        """Test that an admin cannot modify another admin's league."""
        other_league = create_league(admin_user=self.other_admin_user)

        payload = {
            'name': 'Unauthorized Update',
            'season': 'Summer',
            'year': 2023,
            'is_active': False,
        }

        url = detail_url(other_league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        other_league.refresh_from_db()
        self.assertNotEqual(other_league.name, payload['name'])

    def test_admin_can_delete_own_league(self):
        """Test that an admin can delete their own league."""
        league = create_league(admin_user=self.admin_user)

        url = detail_url(league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(League.objects.filter(id=league.id).exists())

    def test_admin_cannot_delete_another_admins_league(self):
        """Test that an admin cannot delete another admin's league."""
        other_league = create_league(admin_user=self.other_admin_user)

        url = detail_url(other_league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(League.objects.filter(id=other_league.id).exists())


class AdditionalAdminLeagueApiTests(TestCase):
    """Test additional admins' permissions in the league API."""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.additional_admin_user = get_user_model().objects.create_user(
            'additionaladmin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_user = get_user_model().objects.create_user(
            'user@example.com',
            'test123',
            is_admin=False,
        )

        self.client.force_authenticate(self.admin_user)

    def test_additional_admin_can_modify_league(self):
        """Test that an additional admin can modify the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'name': 'Updated by Additional Admin',
            'is_active': False,
        }

        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        league.refresh_from_db()
        serializer = LeagueSerializer(league)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(league.name, payload['name'])
        self.assertFalse(league.is_active)

    def test_additional_admin_can_delete_league(self):
        """Test that an additional admin can delete the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        url = detail_url(league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(League.objects.filter(id=league.id).exists())

    def test_non_admin_cannot_modify_league(self):
        """Test that a non-admin user cannot modify the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.other_user)

        payload = {
            'name': 'Unauthorized Update',
            'year': 2024,
        }

        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        league.refresh_from_db()
        self.assertNotEqual(league.name, payload['name'])

    def test_non_admin_cannot_delete_league(self):
        """Test that a non-admin user cannot delete the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.other_user)

        url = detail_url(league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(League.objects.filter(id=league.id).exists())

    def test_main_admin_can_modify_league(self):
        """Test that the main admin can modify the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        payload = {
            'name': 'Main Admin Update',
            'year': 2023,
        }

        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        league.refresh_from_db()
        self.assertEqual(league.name, payload['name'])

    def test_main_admin_can_delete_league(self):
        """Test that the main admin can delete the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        url = detail_url(league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(League.objects.filter(id=league.id).exists())


class UserLeagueApiTests(TestCase):
    """Test league API access for league members."""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.player = create_player()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='test123',
            player_profile=self.player,
            is_admin=False,
        )
        self.other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'test123',
            is_admin=False,
        )

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.team_season = create_team_season(
            team=self.team, season=self.season)
        create_team_player(team_season=self.team_season, player=self.player)

    def test_league_player_can_read_league_detail(self):
        """Test that league user can read the league's details."""
        self.client.force_authenticate(self.user)

        url = detail_url(self.league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = LeagueSerializer(self.league)
        self.assertEqual(res.data, serializer.data)

    def test_non_player_cannot_read_league_detail(self):
        """Test that a non-league user cannot read the league's details."""
        self.client.force_authenticate(self.other_user)

        url = detail_url(self.league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_modify_league(self):
        """Test that a regular user cannot modify the league."""
        self.client.force_authenticate(self.user)

        payload = {
            'name': 'Unauthorized Update',
            'season': 'Spring',
            'year': 2023,
        }

        url = detail_url(self.league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.league.refresh_from_db()
        self.assertNotEqual(self.league.name, payload['name'])

    def test_user_cannot_delete_league(self):
        """Test that a regular user cannot delete the league."""
        self.client.force_authenticate(self.user)

        url = detail_url(self.league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(League.objects.filter(id=self.league.id).exists())

    def test_other_user_cannot_access_league(self):
        """Test non-league user cannot access its details."""
        self.client.force_authenticate(self.other_user)

        url = detail_url(self.league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminSeasonApiTests(TestCase):
    """Test the CRUD operations on seasons for admin users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.additional_admin = get_user_model().objects.create_user(
            'additionaladmin@example.com',
            'test123',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)

        self.league = create_league(admin_user=self.admin_user)

    def test_create_season(self):
        """Test that an admin user can create a season."""
        payload = {
            'name': 'Spring Season',
            'year': 2024,
            'league': self.league.id
        }
        url = seasons_url(self.league.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Season.objects.filter(
            name=payload['name'], league=self.league).exists())

    def test_update_season(self):
        """Test that an admin user can update a season."""
        season = create_season(league=self.league)
        payload = {'name': 'Updated Season'}
        url = season_detail_url(self.league.id, season.id)

        res = self.client.patch(url, payload)
        season.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(season.name, payload['name'])

    def test_delete_season(self):
        """Test that an admin user can delete a season."""
        season = create_season(league=self.league)
        url = season_detail_url(self.league.id, season.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Season.objects.filter(id=season.id).exists())

    def test_additional_admin_can_create_season(self):
        """Test that additional admins can create a league."""
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

        payload = {
            'name': 'New Season',
            'year': 2025,
        }
        url = seasons_url(self.league.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Season.objects.filter(
            name=payload['name'], league=self.league).exists())

    def test_additional_admin_can_update_season(self):
        """Test that additional admins can update a league."""
        season = create_season(league=self.league)
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

        payload = {'name': 'Updated Season'}
        url = reverse('league:season-detail', args=[self.league.id, season.id])
        res = self.client.patch(url, payload)

        season.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(season.name, payload['name'])

    def test_additional_admin_can_delete_season(self):
        """Test that additional admins can delete a league."""
        season = create_season(league=self.league)
        self.league.additional_admins.add(self.additional_admin)
        self.client.force_authenticate(self.additional_admin)

        url = season_detail_url(self.league.id, season.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Season.objects.filter(id=season.id).exists())


class UserSeasonApiTests(TestCase):
    """Test league API access for seasons for regular league members."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.player = create_player()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='test123',
            player_profile=self.player,
            is_admin=False,
        )
        self.other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'test123',
            is_admin=False,
        )

        self.league = create_league(admin_user=self.admin_user)
        self.season = create_season(league=self.league)
        self.team = create_team(league=self.league)
        self.team_season = create_team_season(
            team=self.team, season=self.season)
        create_team_player(team_season=self.team_season, player=self.player)

    def test_league_user_can_read_seasons(self):
        """Test that a league member can list and view seasons."""
        self.client.force_authenticate(self.user)

        url = seasons_url(self.league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(self.season.name, str(res.data))

    def test_non_league_user_cannot_access_seasons(self):
        """Test that a user who is not part of
        the league cannot view the seasons."""
        self.client.force_authenticate(self.other_user)

        url = seasons_url(self.league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_modify_seasons(self):
        """Test that a regular user cannot modify seasons."""
        self.client.force_authenticate(self.user)
        payload = {'name': 'Unauthorized Season'}
        url = season_detail_url(self.league.id, self.season.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        self.season.refresh_from_db()
        self.assertNotEqual(self.season.name, payload['name'])
