import random
from datetime import timedelta, datetime
from core.models import MatchNight, Match, TeamSeason


class ScheduleService:
    def __init__(self, schedule):
        self.schedule = schedule
        self.teams = list(TeamSeason.objects.filter(season=schedule.season))
        random.shuffle(self.teams)
        self.num_weeks = schedule.num_weeks
        self.home_away_tracker = {team.id: {'home': 0, 'away': 0} for team in self.teams}

    def generate_schedule(self):
        """Generate matchups using a rotating round-robin schedule."""
        current_week = 0
        num_teams = len(self.teams)

        assert num_teams % 2 == 0, "Number of teams must be even for scheduling."

        # Split the teams into two halves
        half = num_teams // 2
        list1 = self.teams[:half]
        list2 = self.teams[half:]

        while current_week < self.num_weeks:
            match_night_date = self.get_next_match_date(current_week)
            match_night, _ = MatchNight.objects.get_or_create(
                schedule=self.schedule, date=match_night_date)

            # Alternate home/away between list1 and list2 each week
            if current_week % 2 == 0:
                home_list, away_list = list1, list2
            else:
                home_list, away_list = list2, list1

            # Schedule matches by pairing teams from the two lists
            for i in range(half):
                home_team = home_list[i]
                away_team = away_list[i]
                Match.objects.create(
                    match_night=match_night,
                    home_team=home_team,
                    away_team=away_team,
                    status="Scheduled"
                )
                self.home_away_tracker[home_team.id]['home'] += 1
                self.home_away_tracker[away_team.id]['away'] += 1

            # Rotate the lists for the next week's matchups
            list1.insert(1, list2.pop(0))  # Move first team from list2 to list1
            list2.append(list1.pop(-1))    # Move last team from list1 to the end of list2

            current_week += 1

    def get_next_match_date(self, week_offset):
        """Calculate the date of the match night."""
        if isinstance(self.schedule.start_date, str):
            start_date = datetime.strptime(self.schedule.start_date, '%Y-%m-%d').date()
        else:
            start_date = self.schedule.start_date
        return start_date + timedelta(weeks=week_offset)
