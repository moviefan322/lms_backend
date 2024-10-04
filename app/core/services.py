import random
from datetime import timedelta
from .models import MatchNight, Match, TeamSeason


class ScheduleService:
    def __init__(self, schedule):
        self.schedule = schedule
        self.teams = list(TeamSeason.objects.filter(season=schedule.season))
        random.shuffle(self.teams)
        self.num_weeks = schedule.num_weeks
        self.match_history = self._initialize_match_history()
        self.home_away_tracker = {
            team.id: {'home': 0, 'away': 0} for team in self.teams}

    def generate_schedule(self):
        """Generate a schedule where no team plays
        another twice before all others are played."""
        current_week = 0

        for team1 in self.teams:
            for team2 in self.teams:
                if team1 == team2:
                    continue

                matchup = frozenset([team1.id, team2.id])

                if matchup not in self.match_history:
                    home_count = self.home_away_tracker[team1.id]['home']
                    away_count = self.home_away_tracker[team1.id]['away']

                    if home_count <= away_count:
                        home_team, away_team = team1, team2
                    else:
                        home_team, away_team = team2, team1

                    match_night_date = self.get_next_match_date(current_week)
                    match_night, _ = MatchNight.objects.get_or_create(
                        schedule=self.schedule,
                        date=match_night_date
                    )

                    Match.objects.create(
                        match_night=match_night,
                        home_team=home_team,
                        away_team=away_team,
                        status="Scheduled"
                    )

                    self.match_history.add(matchup)
                    self.home_away_tracker[home_team.id]['home'] += 1
                    self.home_away_tracker[away_team.id]['away'] += 1

                    current_week += 1
                    if current_week >= self.num_weeks:
                        return

    def _initialize_match_history(self):
        """Initialize the match history to track which
        teams have already played each other."""
        return set()

    def get_next_match_date(self, week_offset):
        """Calculate the date of the match night."""
        return self.schedule.start_date + timedelta(weeks=week_offset)
