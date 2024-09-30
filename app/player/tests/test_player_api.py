"""
Tests for player APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Player, League, Team

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
        'captain': create_player(),
    }
    defaults.update(params)

    return Team.objects.create(league=league, **defaults)


class PublicPlayerScoreApiTests(TestCase):
    """Test the player API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PLAYER_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

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

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_players_unauthorized(self):
        """Test retrieving players"""
        league = create_league(create_admin())
        team = create_team(league)
        create_player(name='Test Player 1', handicap=10, teams=[team.id])
        create_player(name='Test Player 2', handicap=15, teams=[team.id])
        self.client.logout()

        res = self.client.get(PLAYER_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_detail_unauthorized(self):
        """Test getting player detail"""
        league = create_league(create_admin())
        team = create_team(league)
        player = create_player(name='Test Player', teams=[team.id])
        self.client.logout()

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


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

    def test_create_player_successful(self):
        """Test that an admin user can create a player"""
        league = create_league(self.admin_user)
        team = create_team(league)
        payload = {
            'name': 'Test Player',
            'handicap': 10,
            'teams': [team.id]
        }
        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(id=res.data['id'])
        self.assertEqual(player.name, payload['name'])
        self.assertEqual(player.handicap, payload['handicap'])

    def test_create_player_invalid(self):
        """Test creating a player with invalid data"""
        league = create_league(self.admin_user)
        team = create_team(league)
        payload = {
            'name': '',
            'handicap': -10,
            'teams': [team.id]
        }
        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_plauers(self):
        """Test retrieving a list of players"""
        league = create_league(self.admin_user)
        team = create_team(name='Test Team', league=league)
        create_player(name='Test Player 1', handicap=10, teams=[team.id])
        create_player(name='Test Player 2', handicap=8, teams=[team.id])

        res = self.client.get(PLAYER_URL)

        players = Player.objects.all().order_by('name')
        serializer = PlayerSerializer(players, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_view_player_detail(self):
        """Test viewing a player detail"""
        league = League.objects.create(name='Test League')
        team = Team.objects.create(name='Test Team', league=league)
        player = Player.objects.create(
            name='Test Player',
            handicap=10,
            team=team
        )

        url = reverse('player:player-detail', args=[player.id])
        res = self.client.get(url)

        serializer = PlayerDetailSerializer(player)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
