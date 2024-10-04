# import random
# from datetime import timedelta
# from .models import MatchNight, Match, TeamSeason


# class ScheduleService:
#     def __init__(self, schedule):
#         self.schedule = schedule
#         self.teams = list(TeamSeason.objects.filter(
#             season=schedule.season))
#         self.num_teams = len(self.teams)
#         self.num_weeks = schedule.num_weeks

#     def generate_schedule(self):
#         """Generates a schedule where no team plays another twice before all others are played."""
#         matches = []
#         played_pairs = set()
#         team_list = self.teams.copy()

#         for week in range(self.num_weeks):
#             random.shuffle(team_list)  # Shuffle teams to ensure randomness
#             week_matches = []

#             for i in range(0, len(team_list), 2):
#                 if i + 1 < len(team_list):
#                     team1, team2 = team_list[i], team_list[i + 1]
#                     matchup = tuple(sorted([team1.id, team2.id]))

#                     if matchup not in played_pairs:
#                         # Assign home/away alternation
#                         if week % 2 == 0:
#                             home_team, away_team = team1, team2
#                         else:
#                             home_team, away_team = team2, team1
                        
#                         # Create the match night if necessary
#                         match_night_date = self.get_next_match_date(week)
#                         match_night, _ = MatchNight.objects.get_or_create(
#                             schedule=self.schedule,
#                             date=match_night_date
#                         )

#                         # Create a new match and add to the schedule
#                         Match.objects.create(
#                             match_night=match_night,
#                             home_team=home_team,
#                             away_team=away_team,
#                             status="Scheduled"
#                         )
                        
#                         week_matches.append(matchup)
#                         played_pairs.add(matchup)

#             # If not all teams have a match, leave one team idle for the week
#             if len(team_list) % 2 != 0:
#                 idle_team = team_list[-1]  # Last team is idle this week
#                 print(f"Week {week + 1}: Team {idle_team.id} is idle.")

#     def get_next_match_date(self, week_offset):
#         """Calculate the date of the match night."""
#         return self.schedule.start_date + timedelta(weeks=week_offset)
