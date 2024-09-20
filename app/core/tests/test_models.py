"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Player, Team, League


def create_league():
    """Create a league."""
    league = League.objects.create(
        name='Test League',
        season='Winter',
        year=2021,
        is_active=True
    )

    return league


def create_player():
    """Create a player."""
    player = Player.objects.create(
        name='Test Player',
        handicap=8,
    )

    return player


def create_team():
    """Create a team."""
    team = Team.objects.create(
        name='Test Team',
        captain=create_player(),
        league=create_league()
    )

    return team


class TestUserModel(TestCase):
    """Test User model and related functionality"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without email raises an error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_admin(self):
        """Test creating an admin."""
        user = get_user_model().objects.create_admin(
            'admin@example.com',
            'test123'
        )

        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)


class TestLeagueModel(TestCase):
    """Test League model and related functionality"""

    def test_create_league(self):
        """Test creating a league."""
        name = 'Test League'
        season = 'Winter'
        year = 2021

        league = League.objects.create(
            name=name,
            season=season,
            year=year,
            is_active=True
        )

        self.assertEqual(league.name, name)
        self.assertEqual(league.season, season)
        self.assertEqual(league.year, year)
        self.assertTrue(league.is_active)

    def test_add_admin_to_league(self):
        """Test adding an admin to a league."""
        league = create_league()
        admin = get_user_model().objects.create_admin(
            'admin@admin.com',
            'test123'
        )

        league.admins.add(admin)

        self.assertIn(admin, league.admins.all())


class TestPlayerModel(TestCase):
    """Test Player model and related functionality"""

    def test_create_player(self):
        """Test creating a player."""
        name = 'Test Player'
        rank = 8

        player = Player.objects.create(
            name=name,
            handicap=rank,
        )

        self.assertEqual(player.name, name)
        self.assertEqual(player.handicap, rank)


class TestTeamModel(TestCase):
    """Test Team model and related functionality"""

    def test_create_team(self):
        """Test creating a team."""
        name = 'Test Team'
        captain = create_player()
        league = create_league()

        team = Team.objects.create(
            name=name,
            captain=captain,
            league=league
        )

        self.assertEqual(team.name, name)
        self.assertEqual(team.captain, captain)
        self.assertEqual(team.league, league)
