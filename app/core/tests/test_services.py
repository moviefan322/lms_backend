import random
from datetime import timedelta
from core.models import MatchNight, Match, TeamSeason


class ScheduleService:
    def __init__(self, schedule):
        self.schedule = schedule
        self.teams = list(TeamSeason.objects.filter(season=schedule.season))
        self.num_weeks = schedule.num_weeks
        self.match_history = self._initialize_match_history()
        self.home_away_tracker = {
            team.id: {'home': 0, 'away': 0} for team in self.teams}
        self.all_matchups = self._generate_all_matchups()

    def _generate_all_matchups(self):
        """Generate all possible matchups between teams,
        ensuring no team plays another twice."""
        matchups = []
        for team1 in self.teams:
            for team2 in self.teams:
                if team1 != team2:
                    matchup = frozenset([team1.id, team2.id])
                    if matchup not in self.match_history:
                        matchups.append((team1, team2))
                        self.match_history.add(matchup)
        random.shuffle(matchups)
        return matchups

    def generate_schedule(self):
        """Distribute all matchups evenly across the available match nights."""
        current_week = 0
        matchup_index = 0

        while current_week < self.num_weeks:
            match_night_date = self.get_next_match_date(current_week)
            match_night, _ = MatchNight.objects.get_or_create(
                schedule=self.schedule,
                date=match_night_date
            )

            matches_for_night = 0
            while (matches_for_night < 2 and
                   matchup_index < len(self.all_matchups)):
                team1, team2 = self.all_matchups[matchup_index]

                home_team = team1 if (
                    self.home_away_tracker[team1.id]['home']
                    <= self.home_away_tracker[team1.id]['away']
                ) else team2
                away_team = team2 if home_team == team1 else team1

                Match.objects.create(
                    match_night=match_night,
                    home_team=home_team,
                    away_team=away_team,
                    status="Scheduled"
                )

                # Update trackers
                self.home_away_tracker[home_team.id]['home'] += 1
                self.home_away_tracker[away_team.id]['away'] += 1
                matches_for_night += 1
                matchup_index += 1

            current_week += 1

    def _initialize_match_history(self):
        """Initialize the match history to track
        which teams have already played each other."""
        return set()

    def get_next_match_date(self, week_offset):
        """Calculate the date of the match night."""
        return self.schedule.start_date + timedelta(weeks=week_offset)
