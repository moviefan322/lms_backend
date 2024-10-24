"""
Database models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


def default_handicap_range():
    return ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def create_admin(self, email, password):
        """Create and return a new admin."""
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    player_profile = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class League(models.Model):
    """League object."""
    name = models.CharField(max_length=255)
    handicap_range = ArrayField(
        models.CharField(max_length=5),
        default=default_handicap_range
    )
    is_active = models.BooleanField(default=True)

    admin = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='leagues_administered'
    )

    additional_admins = models.ManyToManyField(
        get_user_model(),
        related_name='leagues_with_admin_privileges',
        blank=True
    )

    def __str__(self):
        return self.name


class Season(models.Model):
    """Season object. A season is tied to a league and has teams."""
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name='seasons')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'year', 'league')

    def __str__(self):
        return f"{self.name} ({self.year})"

    @property
    def admin(self):
        """Inherit admin from the league."""
        return self.league.admin

    @property
    def additional_admins(self):
        """Inherit additional admins from the league."""
        return self.league.additional_admins.all()


class Team(models.Model):
    """Team object."""
    name = models.CharField(max_length=255)
    league = models.ForeignKey(
        'League',
        on_delete=models.CASCADE,
        related_name='teams'
    )

    def __str__(self):
        return self.name


class TeamSeason(models.Model):
    """Intermediary model for tracking team stats in a specific season."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=False)
    captain = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='teams_captained',
        null=False
    )
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)

    class Meta:
        unique_together = ('team', 'season')

    def __str__(self):
        return f'{self.team.name} in {self.season.name} ({self.season.year})'


class Player(models.Model):
    """Player object."""
    name = models.CharField(max_length=255)
    teams = models.ManyToManyField(
        'TeamSeason',
        through='TeamPlayer',
        related_name='players',
        blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TeamPlayer(models.Model):
    """TeamPlayer object."""
    team_season = models.ForeignKey(
        'TeamSeason',
        on_delete=models.CASCADE,
        related_name='team_players'
    )
    player = models.ForeignKey(
        'Player', on_delete=models.CASCADE, related_name='team_players')
    handicap = models.IntegerField(default=3)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    is_captain = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('team_season', 'player')

    def __str__(self):
        return f'{self.team_season} - {self.player}'


class Schedule(models.Model):
    season = models.OneToOneField(
        Season, on_delete=models.CASCADE, related_name='schedule')
    start_date = models.DateField()
    num_weeks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    default_start_time = models.TimeField(null=False, default='19:00')

    def __str__(self):
        return f"Schedule for {self.season.name}"


class MatchNight(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name='match_nights')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Scheduled')

    class Meta:
        unique_together = ('date', 'schedule')

    def save(self, *args, **kwargs):
        """Override save method to use schedule's
        default start time if not provided."""
        if not self.start_time:
            self.start_time = self.schedule.default_start_time
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.schedule}"


class Match(models.Model):
    match_night = models.ForeignKey(
        MatchNight, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(
        TeamSeason, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(
        TeamSeason, on_delete=models.CASCADE, related_name='away_matches')
    match_time = models.TimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    home_race_to = models.IntegerField(null=True, blank=True)
    away_race_to = models.IntegerField(null=True, blank=True)
    winner = models.CharField(max_length=10, null=True,
                              blank=True)
    status = models.CharField(max_length=50, default='Scheduled')
    team_snapshot = models.JSONField(null=True, blank=True)
    lineups = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('match_night', 'home_team', 'away_team')

    def calculate_race_to(self):
        """Calculate race-to values based on lineups."""
        if self.lineups:
            home_team_handicap = sum(player['handicap']
                                     for player in self.lineups['home_team'])
            away_team_handicap = sum(player['handicap']
                                     for player in self.lineups['away_team'])

            self.home_race_to = max(20, 30 - home_team_handicap)
            self.away_race_to = max(20, 30 - away_team_handicap)
            self.save()

    def set_team_snapshot(self):
        """Store a snapshot of both teams' current records."""
        self.team_snapshot = {
            "home_team": {
                "team_name": self.home_team.team.name,
                "wins": self.home_team.wins,
                "losses": self.home_team.losses,
                "captain": self.home_team.captain.name,
                "games_won": self.home_team.games_won,
                "games_lost": self.home_team.games_lost,
            },
            "away_team": {
                "team_name": self.away_team.team.name,
                "wins": self.away_team.wins,
                "losses": self.away_team.losses,
                "captain": self.away_team.captain.name,
                "games_won": self.away_team.games_won,
                "games_lost": self.away_team.games_lost,
            }
        }

    def update_match_winner(self):
        """Determine the winner based on race-to values."""
        if self.home_score is not None and self.away_score is not None:
            if self.home_score >= self.home_race_to:
                self.winner = 'home'
                self.update_team_records(self.home_team, self.away_team)
            elif self.away_score >= self.away_race_to:
                self.winner = 'away'
                self.update_team_records(self.away_team, self.home_team)

    def update_team_records(self, winning_team, losing_team):
        """Update the win/loss records for TeamSeason."""
        winning_team.wins += 1
        winning_team.games_won += (
            self.home_score if winning_team == self.home_team
            else self.away_score
        )
        losing_team.losses += 1
        losing_team.games_lost += (
            self.home_score if losing_team == self.home_team
            else self.away_score
        )

        winning_team.save()
        losing_team.save()

    def save(self, *args, **kwargs):
        """Override save to inherit match time
        from MatchNight if not provided."""
        if not self.match_time:
            self.match_time = self.match_night.start_time

        if self.status == 'completed':
            self.set_team_snapshot()
            self.update_match_winner()

        super().save(*args, **kwargs)


class Game(models.Model):
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, related_name='games')
    home_player = models.ForeignKey(
        TeamPlayer, on_delete=models.CASCADE, related_name='home_games')
    away_player = models.ForeignKey(
        TeamPlayer, on_delete=models.CASCADE, related_name='away_games')
    home_race_to = models.IntegerField(null=True, blank=True)
    away_race_to = models.IntegerField(null=True, blank=True)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    winner = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=50, default='Scheduled')
    player_snapshot = models.JSONField(null=True, blank=True)

    def update_game_winner(self):
        """Determine the winner based on scores and update match scores."""
        if (self.winner is None and
            self.home_score is not None and
                self.away_score is not None):
            if self.match.home_score is None:
                self.match.home_score = 0
            if self.match.away_score is None:
                self.match.away_score = 0

            if self.home_score >= self.home_race_to:
                self.winner = 'home'
                self.match.home_score += 1
            elif self.away_score >= self.away_race_to:
                self.winner = 'away'
                self.match.away_score += 1
            else:
                self.winner = 'tie'

            self.match.save()

    def set_player_snapshot(self):
        """Store a snapshot of both players' current records."""
        self.player_snapshot = {
            "home_player": {
                "player_name": self.home_player.player.name,
                "wins": self.home_player.wins,
                "losses": self.home_player.losses,
                "handicap": self.home_player.handicap
            },
            "away_player": {
                "player_name": self.away_player.player.name,
                "wins": self.away_player.wins,
                "losses": self.away_player.losses,
                "handicap": self.away_player.handicap
            }
        }

    def save(self, *args, **kwargs):
        """Override save to set race-to values and update winner/status."""
        if self.home_race_to is None:
            self.home_race_to = 1
        if self.away_race_to is None:
            self.away_race_to = 1

        if self.status == 'completed':
            self.set_player_snapshot()
            self.update_game_winner()

        super().save(*args, **kwargs)
