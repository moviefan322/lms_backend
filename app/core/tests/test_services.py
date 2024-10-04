# from django.test import TestCase
# from django.utils import timezone
# from core.models import Schedule, TeamSeason, MatchNight, Match
# from core.services import ScheduleService
# from .test_models import (
#     create_league,
#     create_team,
#     create_season,
#     create_schedule,
#     create_team_season
# )

# class ScheduleServiceTests(TestCase):
#     """Tests for schedule generation logic and validation."""

#     def setUp(self):
#         """Set up basic data for testing."""
#         self.league = create_league()
#         self.season = create_season(self.league)
#         self.start_date = timezone.now().date()
#         self.schedule = create_schedule(
#             self.season, start_date=self.start_date, num_weeks=4
#         )

#         self.team_season1 = create_team_season(
#             create_team(self.league), self.season)
#         self.team_season2 = create_team_season(
#             create_team(self.league), self.season)
#         self.team_season3 = create_team_season(
#             create_team(self.league), self.season)
#         self.team_season4 = create_team_season(
#             create_team(self.league), self.season)

#         self.teams = [self.team_season1, self.team_season2,
#                       self.team_season3, self.team_season4]

#     def test_generate_match_nights(self):
#         """Test that the correct number of match nights are generated."""
#         service = ScheduleService(self.schedule)
#         num_weeks = self.schedule.num_weeks
#         service.generate_schedule()

#         match_nights = MatchNight.objects.filter(schedule=self.schedule)
#         self.assertEqual(match_nights.count(), num_weeks)

#         # Verify match nights start from the correct date
#         for i, night in enumerate(match_nights):
#             expected_date = self.start_date + timezone.timedelta(weeks=i)
#             self.assertEqual(night.date, expected_date)

#     def test_generate_matches_per_night(self):
#         """Test that matches are generated for each night, with no team playing twice per night."""
#         service = ScheduleService(self.schedule)
#         service.generate_schedule()

#         match_nights = MatchNight.objects.filter(schedule=self.schedule)
#         for night in match_nights:
#             matches = Match.objects.filter(match_night=night)
#             # Since we have 4 teams, 2 matches should be created per night
#             self.assertEqual(matches.count(), 2)

#     def test_no_duplicate_matchups_before_all_teams_played(self):
#         """Test that no team plays another team twice until all others have been played."""
#         service = ScheduleService(self.schedule)
#         service.generate_schedule()

#         played_pairs = set()
#         match_nights = MatchNight.objects.filter(schedule=self.schedule)

#         for night in match_nights:
#             matches = Match.objects.filter(match_night=night)
#             for match in matches:
#                 matchup = tuple(
#                     sorted([match.home_team.id, match.away_team.id]))
#                 self.assertNotIn(matchup, played_pairs)
#                 played_pairs.add(matchup)

#     def test_alternating_home_and_away(self):
#         """Test that each team alternates between home and away matches."""
#         service = ScheduleService(self.schedule)
#         service.generate_schedule()

#         home_away_tracker = {team.id: {'home': 0, 'away': 0}
#                              for team in self.teams}

#         match_nights = MatchNight.objects.filter(schedule=self.schedule)

#         for night in match_nights:
#             matches = Match.objects.filter(match_night=night)
#             for match in matches:
#                 home_away_tracker[match.home_team.id]['home'] += 1
#                 home_away_tracker[match.away_team.id]['away'] += 1

#         for team_id, counts in home_away_tracker.items():
#             self.assertTrue(abs(counts['home'] - counts['away']) <= 1,
#                             f"Team {team_id} home/away imbalance: {counts}")

#     def test_even_matchups(self):
#         """Test that every team plays each other evenly across the schedule."""
#         service = ScheduleService(self.schedule)
#         service.generate_schedule()

#         match_counts = {team.id: 0 for team in self.teams}

#         match_nights = MatchNight.objects.filter(schedule=self.schedule)
#         for night in match_nights:
#             matches = Match.objects.filter(match_night=night)
#             for match in matches:
#                 match_counts[match.home_team.id] += 1
#                 match_counts[match.away_team.id] += 1

#         for team_id, count in match_counts.items():
#             # Each team should play evenly based on the number of weeks and teams.
#             self.assertEqual(count, self.schedule.num_weeks)
