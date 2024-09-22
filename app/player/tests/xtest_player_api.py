"""
Tests for player APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Player

from player.serializers import PlayerSerializer, PlayerDetailSerializer

PLAYER_URL = reverse('player:player-list')


class PublicPlayerScoreApiTests(TestCase):
    """Test the player API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PLAYER_URL)

    def test_create_player_unauthorized(self):
        """Test that admin auth is required for creating a player"""
        payload = {
            'name': 'Test Player',
            'handicap': 10
        }

        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_players_unauthorized(self):
        """Test retrieving players"""
        Player.objects.create(name='Test Player 1', handicap=10)
        Player.objects.create(name='Test Player 2', handicap=15)

        res = self.client.get(PLAYER_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_player_detail_unauthorized(self):
        """Test getting player detail"""
        player = Player.objects.create(name='Test Player', handicap=10)

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
        self.client.force_authenticate(self.admin_user)

    def test_create_player_successful(self):
        """Test that an admin user can create a player"""
        payload = {
            'name': 'Test Player',
            'handicap': 10
        }
        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(id=res.data['id'])
        self.assertEqual(player.name, payload['name'])
        self.assertEqual(player.handicap, payload['handicap'])

    def test_create_player_invalid(self):
        """Test creating a player with invalid data"""
        payload = {
            'name': '',
            'handicap': -10
        }
        res = self.client.post(PLAYER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
