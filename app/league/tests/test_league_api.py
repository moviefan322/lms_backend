"""
Tests league API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import League
from league.serializers import LeagueSerializer
from core.tests.test_models import random_string, create_admin

LEAGUES_URL = reverse('league:league-list')


def detail_url(league_id):
    """Return league detail URL."""
    return reverse('league:league-detail', args=[league_id])


def create_league(admin_user, **params):
    """Helper function to create a league with the provided admin user."""
    defaults = {
        'name': random_string(),
        'season': 'Winter',
        'year': 2021,
        'is_active': True,
    }
    defaults.update(params)

    return League.objects.create(admin=admin_user, **defaults)


class PublicLeagueApiTests(TestCase):
    """Test the public access to the league API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_leagues_unauthorized(self):
        """Test retrieving leagues without authentication should fail."""
        res = self.client.get(LEAGUES_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_league_detail_unauthorized(self):
        """Test getting league detail without authentication should fail."""
        league = create_league(create_admin())

        url = detail_url(league.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_league_unauthorized(self):
        """Test creating a league without authentication should fail."""
        payload = {
            'name': 'Test League',
            'season': 'Winter',
            'year': 2021,
            'is_active': True,
        }

        res = self.client.post(LEAGUES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


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

    def test_create_league_successful(self):
        """Test that an admin user can create a league."""
        payload = {
            'name': 'Test League',
            'season': 'Winter',
            'year': 2021,
            'is_active': True,
        }
        res = self.client.post(LEAGUES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        league = League.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(league, key))
        # Check admin is set correctly
        self.assertEqual(league.admin, self.admin_user)

    def test_update_league(self):
        """Test updating a league."""
        league = create_league(admin_user=self.admin_user)
        payload = {
            'name': 'Updated League',
            'season': 'Fall',
            'year': 2020,
            'is_active': False,
        }
        url = detail_url(league.id)
        self.client.patch(url, payload)

        league.refresh_from_db()
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
