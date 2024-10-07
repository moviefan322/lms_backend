from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Schedule
from core.tests.test_models import create_admin
from .test_helpers import create_league, create_season
from django.contrib.auth import get_user_model
from datetime import date


def schedule_url(league_id, season_id, schedule_id):
    """Return the schedule URL for a given league, season, and schedule."""
    return reverse('league:schedule-detail',
                   args=[league_id, season_id, schedule_id])


def schedule_list_url(league_id, season_id):
    """Return the schedule list URL for a given league and season."""
    return reverse('league:schedule-list', args=[league_id, season_id])


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

        url = schedule_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_admin_can_view_schedule(self):
        """Test that an admin user can view a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_admin_can_modify_schedule(self):
        """Test that an admin user can modify a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['num_weeks'], 6)

    def test_admin_can_delete_schedule(self):
        """Test that an admin user can delete a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


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

        url = schedule_list_url(self.league.id, self.season.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_additional_admin_can_view_schedule(self):
        """Test that an additional admin user can view a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_additional_admin_can_modify_schedule(self):
        """Test that an additional admin user can modify a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['num_weeks'], 6)

    def test_additional_admin_can_delete_schedule(self):
        """Test that an additional admin user can delete a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id, schedule.id)
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
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('start_date', res.data)
        self.assertEqual(res.data['start_date'], '2024-10-01')

    def test_user_cannot_modify_schedule(self):
        """Test that a regular user cannot modify a schedule."""
        schedule = Schedule.objects.create(
            season=self.season,
            start_date=date(2024, 10, 1),
            num_weeks=4,
            default_start_time='19:00'
        )

        payload = {'num_weeks': 6}

        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
