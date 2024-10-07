from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Schedule, League, Season
from core.tests.test_models import create_league, create_season, create_admin
from django.contrib.auth import get_user_model
from datetime import date


def schedule_url(league_id, season_id, schedule_id):
    """Return the schedule URL for a given league, season, and schedule."""
    return reverse('league:schedule-detail', args=[league_id, season_id, schedule_id])


class UserScheduleApiTests(TestCase):
    """Test schedule access for regular users."""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_admin()
        self.client.force_authenticate(self.admin_user)

        self.league = create_league()
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
        
        # Correct the URL to pass the schedule_id
        url = schedule_url(self.league.id, self.season.id, schedule.id)
        res = self.client.patch(url, payload)

        self.assertEqual
