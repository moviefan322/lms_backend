# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from core.models import Schedule, Season, League, TeamSeason
# from league.services import ScheduleService

# class ScheduleServiceTests(TestCase):
#     def setUp(self):
#         # Setup data needed for schedule service tests, like creating a league and season
#         self.league = create_league()
#         self.season = create_season(self.league)
#         self.schedule = create_schedule(self.season, start_date=timezone.now(), num_weeks=4)
    
#     def test_generate_schedule(self):
#         # Test the schedule generation service
#         service = ScheduleService(self.schedule)
#         service.generate_schedule()
#         self.assertEqual(Match.objects.count(), self.schedule.num_weeks * 2)

#     def test_no_duplicate_matchups(self):
#         # Add more granular tests for matchup validation
#         pass

# class ScheduleAPITests(TestCase):
#     def setUp(self):
#         # Setup the API client, URL endpoints, and any mock data
#         self.client = APIClient()
#         self.league = create_league()
#         self.season = create_season(self.league)
#         self.schedule_url = reverse('schedule-list')  # Adjust as per your API structure
    
#     def test_create_schedule(self):
#         # Test creating a schedule via the API
#         payload = {'season': self.season.id, 'start_date': '2024-01-01', 'num_weeks': 6}
#         response = self.client.post(self.schedule_url, payload)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_modify_schedule(self):
#         # Test modifying a schedule via the API
#         schedule = create_schedule(self.season)
#         url = reverse('schedule-detail', args=[schedule.id])
#         payload = {'num_weeks': 8}
#         response = self.client.patch(url, payload)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
