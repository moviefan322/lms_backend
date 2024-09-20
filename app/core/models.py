"""
Database models
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


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
        blank=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class League(models.Model):
    """League object."""
    name = models.CharField(max_length=255)
    season = models.CharField(max_length=255)
    year = models.IntegerField()
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


class Team(models.Model):
    """Team object."""
    name = models.CharField(max_length=255)
    league = models.ForeignKey(
        'League',
        on_delete=models.CASCADE,
        related_name='teams'
    )
    captain = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='teams_captained',
        null=False
    )

    def __str__(self):
        return self.name


class Player(models.Model):
    """Player object."""
    name = models.CharField(max_length=255)
    teams = models.ManyToManyField(
        'Team',
        related_name='players',
        blank=True
    )
    handicap = models.IntegerField(default=3)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return self.name
