"""
Tests for models
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from core.models import Player, Team, League

import random
import string


def random_string(length=5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def create_admin():
    """Create an admin."""

    return get_user_model().objects.create_admin(
        random_string() + '@example.com',
        'test123'
    )


def create_user():
    """Create a user."""

    return get_user_model().objects.create_user(
        random_string() + '@example.com',
        'test123'
    )


def create_league():
    """Create a league."""
    league = League.objects.create(
        name=random_string(),
        season='Winter',
        year=2021,
        is_active=True,
        admin=create_admin()
    )

    return league


def create_player():
    """Create a player."""
    player = Player.objects.create(
        name=random_string(),
        handicap=8,
    )

    return player


def create_team():
    """Create a team."""
    team = Team.objects.create(
        name=random_string(),
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

    def test_user_email_uniqueness(self):
        """Test that creating a user with a duplicate email raises an error."""
        email = 'test@example.com'
        get_user_model().objects.create_user(
            email=email,
            password='password123',
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=email,
                password='password123',
            )


class TestLeagueModel(TestCase):
    """Test League model and related functionality"""

    def test_create_league(self):
        """Test creating a league."""
        name = 'Test League'
        season = 'Winter'
        year = 2021
        admin = create_admin()

        league = League.objects.create(
            name=name,
            season=season,
            year=year,
            is_active=True,
            admin=admin
        )

        self.assertEqual(league.name, name)
        self.assertEqual(league.season, season)
        self.assertEqual(league.year, year)
        self.assertTrue(league.is_active)

    def test_add_admin_to_league(self):
        """Test adding an admin to a league."""
        league = create_league()

        additional_admin = create_user()
        league.additional_admins.add(additional_admin)

        self.assertIn(additional_admin, league.additional_admins.all())

    def test_prevent_duplicate_player_in_team(self):
        """Test that a player cannot be added to a team multiple times."""
        player = create_player()
        team = create_team()

        player.teams.add(team)
        player.teams.add(team)

        self.assertEqual(player.teams.filter(id=team.id).count(), 1)


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

    def test_create_team_without_captain_fails(self):
        """Test that creating a team without a captain raises an error."""
        league = create_league()
        with self.assertRaises(IntegrityError):
            Team.objects.create(name='Team Without Captain', league=league)


class TestModelRelationships(TestCase):
    """Test the many-to-many relationship between Player and Team"""

    def test_player_added_to_multiple_teams(self):
        """Test a player can belong to multiple teams."""
        player = create_player()
        team1 = create_team()
        team2 = create_team()

        player.teams.add(team1, team2)

        self.assertIn(team1, player.teams.all())
        self.assertIn(team2, player.teams.all())
        self.assertIn(player, team1.players.all())
        self.assertIn(player, team2.players.all())

    def test_delete_league_deletes_teams(self):
        """Test that deleting a league also deletes associated teams."""
        league = create_league()
        Team.objects.create(
            name='Test Team',
            captain=create_player(),
            league=league
        )
        Team.objects.create(
            name='Test Team2',
            captain=create_player(),
            league=league
        )

        league_id = league.id

        league.delete()

        self.assertEqual(Team.objects.filter(league_id=league_id).count(), 0)
