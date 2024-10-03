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
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
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
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('team_season', 'player')

    def __str__(self):
        return f'{self.team_season} - {self.player}'


class Schedule(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
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
        TeamSeason, on_delete=models.CASCADE, related_name='matches_as_team_a')
    away_team = models.ForeignKey(
        TeamSeason, on_delete=models.CASCADE, related_name='matches_as_team_b')
    match_time = models.TimeField()
    result = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='Scheduled')

    class Meta:
        unique_together = ('match_night', 'home_team', 'away_team')

    def save(self, *args, **kwargs):
        """Override save to inherit match time
        from MatchNight if not provided."""
        if not self.match_time:
            self.match_time = self.match_night.start_time
        super().save(*args, **kwargs)
