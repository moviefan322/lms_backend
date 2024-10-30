"""
Tests for player APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Player,
    League,
    Team, Season,
    TeamSeason,
    TeamPlayer
)

from player.serializers import PlayerSerializer, PlayerDetailSerializer
from core.tests.test_models import random_string, create_admin

PLAYER_URL = reverse('player:player-list')


def create_league(admin_user, **params):
    """Create and return a sample league"""
    defaults = {
        'name': random_string(),
        'is_active': True,
    }
    defaults.update(params)

    return League.objects.create(admin=admin_user, **defaults)


def create_season(league, **params):
    """Create and return a sample season"""
    defaults = {
        'name': random_string(),
        'league': league,
        'year': 2021,
    }
    defaults.update(params)

    return Season.objects.create(**defaults)


def create_player(**params):
    """Create and return a sample player"""
    defaults = {
        'name': random_string(),
    }
    defaults.update(params)

    return Player.objects.create(**defaults)


def create_team(league, **params):
    """Create and return a sample team"""
    defaults = {
        'name': random_string(),
        'league': league,
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Create and return a sample team season"""
    defaults = {
        'name': random_string(),
        'team': team,
        'season': season,
    }
    defaults.update(params)

    return TeamSeason.objects.create(**defaults)


def create_team_player(player, team_season, **params):
    """Create and return a sample team player"""
    defaults = {
        'player': player,
        'team_season': team_season,
    }
    defaults.update(params)

    return TeamPlayer.objects.create(**defaults)


class PublicPlayerScoreApiTests(TestCase):
    """Test the player API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PLAYER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_player_unauthorized(self):
        """Test that admin auth is required for creating a player"""
        league = create_league(create_admin())
        team = create_team(league)
        self.client.logout()
        payload = {
            'name': 'Test Player',
            'handicap': 10,
            'teams': [team.id]
        }

        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_players_unauthorized(self):
        """Test retrieving players"""
        create_player()
        create_player()
        self.client.logout()

        res = self.client.get(PLAYER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_player_detail_unauthorized(self):
        """Test getting player detail"""
        player = create_player()
        self.client.logout()

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminPlayerApiTests(TestCase):
    """Test the authorized admin user player API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email='admin@example.com',
            password='password123',
            is_admin=True
        )
        self.other_admin_user = get_user_model().objects.create_user(
            'otheradmin@example.com',
            'test123',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)

    def test_retrieve_players_by_league(self):
        """Test retrieving players that belong to a specific league"""
        league1 = create_league(admin_user=self.admin_user, name='League 1')
        league2 = create_league(admin_user=self.admin_user, name='League 2')

        season1 = create_season(league=league1)
        season2 = create_season(league=league2)

        team1 = create_team(league=league1)
        team2 = create_team(league=league2)

        captain1 = create_player(name='Captain 1')
        team_season1 = create_team_season(
            team=team1, season=season1, captain=captain1)
        team_season2 = create_team_season(
            team=team2, season=season2, captain=create_player())

        player1 = create_player(name='Player 1')
        player2 = create_player(name='Player 2')
        create_team_player(player1, team_season1)
        create_team_player(player2, team_season2)

        url = reverse('player:player-by-league',
                      kwargs={'league_id': league1.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[1]['name'], player1.name)
        self.assertEqual(res.data[0]['name'], captain1.name)

    def test_retrieve_players_by_league_no_players(self):
        """Test retrieving players when there
        are no players in the specified league"""
        league = create_league(admin_user=self.admin_user, name='Empty League')

        url = reverse('player:player-by-league', args=[league.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_retrieve_players_by_league_unauthorized(self):
        """Test that an unauthorized user cannot retrieve players by league"""
        league = create_league(admin_user=self.admin_user,
                               name='Unauthorized League')
        self.client.logout()

        url = reverse('player:player-by-league', args=[league.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_player_successful(self):
        """Test that an admin user can create a player"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)

        team_season = TeamSeason.objects.create(
            team=team,
            name='Test Team Season',
            season=season,
            captain=create_player(name='Captain')
        )

        payload = {
            'name': 'Test Player',
            'is_active': True,
            'team_season': team_season.id
        }

        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(id=res.data['id'])
        self.assertEqual(player.name, payload['name'])
        self.assertEqual(player.is_active, payload['is_active'])

        team_player = TeamPlayer.objects.get(
            player=player, team_season=team_season)
        self.assertIsNotNone(team_player)

    def test_create_player_invalid(self):
        """Test creating a player with invalid data"""
        payload = {
            'name': '',
            'handicap': -10,
        }
        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_players(self):
        """Test retrieving a list of players"""
        create_player()
        create_player()

        res = self.client.get(PLAYER_URL)

        players = Player.objects.all().order_by('name')
        serializer = PlayerSerializer(players, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_view_player_detail(self):
        """Test viewing a player detail"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        player = create_player()
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.get(url)

        serializer = PlayerDetailSerializer(player)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_partial_update_player(self):
        """Test updating a player with patch"""
        player = create_player()
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        payload = {
            'is_active': False,
        }

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.patch(url, payload)

        player.refresh_from_db()
        self.assertFalse(player.is_active)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update_player(self):
        """Test updating a player with put"""
        player = create_player()
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        payload = {
            'name': 'Updated Player',
            'is_active': False,
        }

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.put(url, payload)

        player.refresh_from_db()
        self.assertEqual(player.name, payload['name'])
        self.assertFalse(player.is_active)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdditionalAdminPlayerApiTests(TestCase):
    """Test the authorized additional admin user player API"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'additional_admin@example.com',
            'testpass123',
            is_admin=True
        )
        self.other_admin_user = get_user_model().objects.create_user(
            'additional_admin2@example.com',
            'testpass123',
            is_admin=True,
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_player_successful(self):
        """Test that an additional admin user can create a player"""
        league = create_league(self.admin_user)
        league.additional_admins.add(self.other_admin_user)
        season = create_season(league)
        team = create_team(league)

        team_season = TeamSeason.objects.create(
            team=team,
            name='Test Team Season',
            season=season,
            captain=create_player(name='Captain')
        )

        self.client.force_authenticate(self.other_admin_user)

        payload = {
            'name': 'Test Player',
            'is_active': True,
            'team_season': team_season.id
        }

        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(id=res.data['id'])
        self.assertEqual(player.name, payload['name'])
        self.assertEqual(player.is_active, payload['is_active'])

        team_player = TeamPlayer.objects.get(
            player=player, team_season=team_season)
        self.assertIsNotNone(team_player)


class UserPlayerApiTests(TestCase):
    """Test the authorized user player API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'example_user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_players(self):
        """Test retrieving a list of players"""

        player1 = create_player(name='Player 1')
        player2 = create_player(name='Player 2')

        league = create_league(create_admin())
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player1, team_season)
        create_team_player(player2, team_season)

        self.user.player_profile = player1
        self.user.save()

        res = self.client.get(PLAYER_URL)

        players = Player.objects.all().order_by('name')
        serializer = PlayerSerializer(players, many=True)

        sorted_response_data = sorted(res.data, key=lambda x: x['id'])
        sorted_serializer_data = sorted(serializer.data, key=lambda x: x['id'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted_response_data, sorted_serializer_data)
        self.assertEqual(len(res.data), 3)

    def test_view_player_detail(self):
        """Test viewing a player detail"""
        league = create_league(create_admin())
        season = create_season(league)
        team = create_team(league)
        player = create_player(name="Test Player")

        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        self.user.player_profile = player
        self.user.save()

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.get(url)

        serializer = PlayerDetailSerializer(player)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_can_modify_own_player_data(self):
        """Test that a user can modify their own player data"""
        player = create_player(name='Player 1')
        league = create_league(create_admin())
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        self.user.player_profile = player
        self.user.save()

        payload = {
            'is_active': False,
        }

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.patch(url, payload)

        player.refresh_from_db()
        self.assertFalse(player.is_active)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_cannot_modify_other_player_data(self):
        """Test that a user cannot modify another player's data"""
        player = create_player(name='Player 1')
        league = create_league(create_admin())
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(player, team_season)

        other_team = create_team(league)
        other_player = create_player(name='Player 2')
        other_team_season = create_team_season(
            other_team, season, captain=create_player())
        create_team_player(other_player, other_team_season)

        self.user.player_profile = player
        self.user.save()

        payload = {
            'is_active': False,
        }

        url = reverse('player:player-detail', args=[other_player.id])
        res = self.client.patch(url, payload)

        other_player.refresh_from_db()
        self.assertTrue(other_player.is_active)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
