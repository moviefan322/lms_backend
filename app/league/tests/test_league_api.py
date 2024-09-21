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
            'season': 'Fall',
            'year': 2020,
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
            'season': 'Fall',
            'year': 2023,
            'is_active': False,
        }

        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        league.refresh_from_db()
        serializer = LeagueSerializer(league)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(league.name, payload['name'])
        self.assertEqual(league.season, payload['season'])
        self.assertEqual(league.year, payload['year'])
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
            'season': 'Spring',
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
            'season': 'Spring',
            'year': 2023,
        }

        url = detail_url(league.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        league.refresh_from_db()
        self.assertEqual(league.name, payload['name'])
        self.assertEqual(league.season, payload['season'])
        self.assertEqual(league.year, payload['year'])

    def test_main_admin_can_delete_league(self):
        """Test that the main admin can delete the league."""
        league = create_league(admin_user=self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        url = detail_url(league.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(League.objects.filter(id=league.id).exists())


# class UserLeagueApiTests(TestCase):
#     """Test league API access for league members."""

#     def setUp(self):
#         self.client = APIClient()

#         self.admin_user = get_user_model().objects.create_user(
#             'admin@example.com',
#             'test123',
#             is_admin=True,
#         )
#         self.user = get_user_model().objects.create_user(
#             'user@example.com',
#             'test123',
#             is_admin=False,
#         )
#         self.other_user = get_user_model().objects.create_user(
#             'otheruser@example.com',
#             'test123',
#             is_admin=False,
#         )

#         self.league = create_league(admin_user=self.admin_user)
#         self.league.players.add(self.user)

#     def test_user_can_read_league_detail(self):
#         """Test that league user can read the league's details."""
#         self.client.force_authenticate(self.user)

#         url = detail_url(self.league.id)
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)

#         serializer = LeagueSerializer(self.league)
#         self.assertEqual(res.data, serializer.data)

#     def test_user_cannot_modify_league(self):
#         """Test that a regular user cannot modify the league."""
#         self.client.force_authenticate(self.user)

#         payload = {
#             'name': 'Unauthorized Update',
#             'season': 'Spring',
#             'year': 2023,
#         }

#         url = detail_url(self.league.id)
#         res = self.client.patch(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

#         self.league.refresh_from_db()
#         self.assertNotEqual(self.league.name, payload['name'])

#     def test_user_cannot_delete_league(self):
#         """Test that a regular user cannot delete the league."""
#         self.client.force_authenticate(self.user)

#         url = detail_url(self.league.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

#         self.assertTrue(League.objects.filter(id=self.league.id).exists())

#     def test_other_user_cannot_access_league(self):
#         """Test non-league user cannot access its details."""
#         self.client.force_authenticate(self.other_user)

#         url = detail_url(self.league.id)
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
