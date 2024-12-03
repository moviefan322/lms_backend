"""
Tests for models
"""
from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from core.models import (
    Player,
    Team,
    League,
    Season,
    TeamSeason,
    TeamPlayer,
    Match,
    MatchNight,
    Schedule,
    Game
)
from django.utils import timezone
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


def create_season(league, **params):
    """Create and return a sample season"""
    defaults = {
        'name': random_string(),
        'year': 2021,
        'league': league,
    }
    defaults.update(params)

    return Season.objects.create(**defaults)


def create_league():
    """Create a league."""
    league = League.objects.create(
        name=random_string(),
        is_active=True,
        admin=create_admin()
    )

    return league


def create_player():
    """Create a player."""
    player = Player.objects.create(
        name=random_string(),
    )

    return player


def create_team(league, **params):
    """Create and return a sample team"""
    defaults = {
        'name': random_string(),
        'league': league,
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_team_player(team_season, **params):
    """Create and return a sample TeamPlayer."""
    defaults = {
        'player': create_player(),
        'team_season': team_season,
    }
    defaults.update(params)

    return TeamPlayer.objects.create(**defaults)


def create_schedule(season, **params):
    """Create and return a sample Schedule."""
    defaults = {
        'season': season,
        'start_date': timezone.now().date(),
        'num_weeks': 8,
    }
    defaults.update(params)

    return Schedule.objects.create(**defaults)


def create_match_night(schedule, **params):
    """Create and return a sample MatchNight."""
    defaults = {
        'date': timezone.now().date(),
        'schedule': schedule,
        'start_time': schedule.default_start_time
    }
    defaults.update(params)

    return MatchNight.objects.create(**defaults)


def create_match(match_night, team1, team2, **params):
    """Create and return a sample Match."""
    defaults = {
        'home_team': team1,
        'away_team': team2,
        'match_night': match_night,
    }
    defaults.update(params)

    return Match.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Create and return a sample TeamSeason."""
    defaults = {
        'team': team,
        'season': season,
        'captain': create_player(),
    }
    defaults.update(params)

    return TeamSeason.objects.create(**defaults)


def create_game(match, home_player, away_player, **params):
    """Create and return a game."""
    defaults = {
        'home_player': home_player,
        'away_player': away_player,
        'home_score': 1,
        'away_score': 0,
        'status': 'completed',
        'home_race_to': 1,
        'away_race_to': 1
    }
    defaults.update(params)

    return Game.objects.create(match=match, **defaults)


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
        admin = create_admin()

        league = League.objects.create(
            name=name,
            is_active=True,
            admin=admin
        )

        self.assertEqual(league.name, name)
        self.assertTrue(league.is_active)

    def test_add_admin_to_league(self):
        """Test adding an admin to a league."""
        league = create_league()

        additional_admin = create_user()
        league.additional_admins.add(additional_admin)

        self.assertIn(additional_admin, league.additional_admins.all())

    def test_prevent_duplicate_player_in_team(self):
        """Test that a player cannot be added to a team
        multiple times in the same season."""
        player = create_player()
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        player.teams.add(team_season)

        player.teams.add(team_season)

        self.assertEqual(player.teams.filter(id=team_season.id).count(), 1)


class TestPlayerModel(TestCase):
    """Test Player model and related functionality"""

    def test_create_player(self):
        """Test creating a player."""
        name = 'Test Player'

        player = Player.objects.create(
            name=name,
        )

        self.assertEqual(player.name, name)

    def test_create_player_with_email(self):
        """Test creating a player with an email."""
        email = 'bob@example.com'
        name = 'Bob'

        player = Player.objects.create(
            name=name,
            email=email
        )

        self.assertEqual(player.email, email)


class TestTeamModel(TestCase):
    """Test Team model and related functionality"""

    def test_create_team(self):
        """Test creating a team."""
        name = 'Test Team'
        league = create_league()

        team = Team.objects.create(
            name=name,
            league=league
        )

        self.assertEqual(team.name, name)


class TestModelRelationships(TestCase):
    """Test the many-to-many relationship between Player and Team"""

    def test_player_added_to_multiple_teams(self):
        """Test a player can belong to multiple teams."""
        player = create_player()
        league1 = create_league()
        league2 = create_league()
        season1 = create_season(league=league1)
        season2 = create_season(league=league2)

        team1 = create_team(league=league1)
        team2 = create_team(league=league2)

        team_season1 = TeamSeason.objects.create(
            team=team1, season=season1, captain=create_player())
        team_season2 = TeamSeason.objects.create(
            team=team2, season=season2, captain=create_player())

        player.teams.add(team_season1, team_season2)

        self.assertIn(team_season1, player.teams.all())
        self.assertIn(team_season2, player.teams.all())
        self.assertIn(player, team_season1.players.all())
        self.assertIn(player, team_season2.players.all())

    def test_delete_league_deletes_teams(self):
        """Test that deleting a league also deletes associated teams."""
        league = create_league()

        Team.objects.create(
            name='Test Team',
            league=league
        )
        Team.objects.create(
            name='Test Team2',
            league=league
        )

        league_id = league.id

        league.delete()

        self.assertEqual(Team.objects.filter(
            league_id=league_id
        ).count(), 0)


class TestSeasonModel(TestCase):
    """Test Season model and related functionality"""

    def test_create_season(self):
        """Test creating a season."""
        league = create_league()
        season = create_season(league=league, name='Spring Season', year=2024)

        self.assertEqual(season.name, 'Spring Season')
        self.assertEqual(season.year, 2024)
        self.assertEqual(season.league, league)

    def test_unique_together_constraint_on_season(self):
        """Test that the same season name
        cannot exist for the same league and year."""
        league = create_league()
        create_season(league=league, name='Winter Season', year=2024)

        with self.assertRaises(IntegrityError):
            create_season(league=league, name='Winter Season', year=2024)


class TestTeamSeasonModel(TestCase):
    """Test TeamSeason model and related functionality"""

    def test_create_team_season(self):
        """Test creating a team season entry."""
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        self.assertEqual(team_season.team, team)
        self.assertEqual(team_season.season, season)
        self.assertEqual(team_season.wins, 0)
        self.assertEqual(team_season.losses, 0)

    def test_team_season_wins_losses(self):
        """Test updating team season stats."""
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team,
            season=season,
            wins=10,
            losses=5,
            captain=create_player()
        )

        self.assertEqual(team_season.wins, 10)
        self.assertEqual(team_season.losses, 5)

        # Update stats
        team_season.wins += 1
        team_season.losses += 1
        team_season.save()

        self.assertEqual(team_season.wins, 11)
        self.assertEqual(team_season.losses, 6)

    def test_team_season_games_won_games_lost(self):
        """Test updating team season stats."""
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team,
            season=season,
            games_won=10,
            games_lost=5,
            captain=create_player()
        )

        self.assertEqual(team_season.games_won, 10)
        self.assertEqual(team_season.games_lost, 5)

        team_season.games_won += 1
        team_season.games_lost += 1
        team_season.save()

        self.assertEqual(team_season.games_won, 11)
        self.assertEqual(team_season.games_lost, 6)

    def test_duplicate_team_in_same_season(self):
        """Test that a team cannot be added
        multiple times to the same season."""
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        with self.assertRaises(IntegrityError):
            TeamSeason.objects.create(team=team, season=season)


class TestTeamPlayerModel(TestCase):
    """Test TeamPlayer model and related functionality"""

    def test_create_team_player(self):
        """Test creating a TeamPlayer entry."""
        player = create_player()
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        team_player = TeamPlayer.objects.create(
            player=player,
            team_season=team_season,
            handicap=5,
            wins=7,
            losses=3
        )

        self.assertEqual(team_player.player, player)
        self.assertEqual(team_player.team_season, team_season)
        self.assertEqual(team_player.handicap, 5)
        self.assertEqual(team_player.wins, 7)
        self.assertEqual(team_player.losses, 3)

    def test_prevent_duplicate_team_player_in_same_team_season(self):
        """Test that a player cannot be added
        multiple times to the same team season."""
        player = create_player()
        league = create_league()
        season = create_season(league=league)
        team = create_team(league=league)

        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        TeamPlayer.objects.create(player=player, team_season=team_season)

        with self.assertRaises(IntegrityError):
            TeamPlayer.objects.create(player=player, team_season=team_season)


class ScheduleModelTests(TestCase):
    """Test Schedule model functionality"""

    def test_create_schedule(self):
        """Test creating a Schedule is successful"""
        league = create_league()
        season = create_season(league)
        schedule = create_schedule(season)

        self.assertEqual(schedule.season, season)


class MatchNightModelTests(TestCase):
    """Test MatchNight model functionality"""

    def test_create_match_night(self):
        """Test creating a MatchNight with default start time."""
        league = create_league()
        season = create_season(league)
        schedule = create_schedule(season, default_start_time='18:00')
        match_night = create_match_night(schedule)

        self.assertEqual(match_night.schedule, schedule)
        self.assertEqual(match_night.start_time, schedule.default_start_time)

    def test_create_match_night_with_custom_start_time(self):
        """Test creating a MatchNight with custom start time."""
        league = create_league()
        season = create_season(league)
        schedule = create_schedule(season)
        custom_time = '20:00'
        match_night = create_match_night(schedule, start_time=custom_time)

        self.assertEqual(match_night.start_time, custom_time)

    def test_match_night_unique_constraint(self):
        """Test the same match night cannot be added twice for a schedule."""
        league = create_league()
        season = create_season(league)
        schedule = create_schedule(season)

        create_match_night(schedule, date=timezone.now().date())

        with self.assertRaises(IntegrityError):
            create_match_night(schedule, date=timezone.now().date())


class MatchModelTests(TestCase):
    """Test Match model functionality"""

    def test_create_match(self):
        """Test creating a Match is successful"""
        league = create_league()
        season = create_season(league)
        team1 = create_team(league)
        team2 = create_team(league)
        team_season1 = create_team_season(team1, season)
        team_season2 = create_team_season(team2, season)
        schedule = create_schedule(season)
        match_night = create_match_night(schedule)
        match = create_match(match_night, team_season1, team_season2)

        self.assertEqual(match.home_team, team_season1)
        self.assertEqual(match.away_team, team_season2)
        self.assertEqual(match.match_night, match_night)

    def test_match_unique_constraint(self):
        """Test that the same match cannot be created twice"""
        league = create_league()
        season = create_season(league)
        team1 = create_team(league)
        team2 = create_team(league)
        team_season1 = create_team_season(team1, season)
        team_season2 = create_team_season(team2, season)

        schedule = create_schedule(season)
        match_night = create_match_night(schedule)

        create_match(match_night, team_season1, team_season2)

        with self.assertRaises(IntegrityError):
            create_match(match_night, team_season1, team_season2)

    def test_match_winner(self):
        """Test updating the winner of a match."""
        league = create_league()
        season = create_season(league)
        team1 = create_team(league)
        team2 = create_team(league)
        team_season1 = create_team_season(team1, season)
        team_season2 = create_team_season(team2, season)

        schedule = create_schedule(season)
        match_night = create_match_night(schedule)
        match = create_match(match_night, team_season1, team_season2)

        match.winner = 'Home'
        match.save()

        self.assertEqual(match.winner, 'Home')

        match.winner = 'Away'
        match.save()

        self.assertEqual(match.winner, 'Away')

    def test_update_team_records(self):
        """Test that team records are updated correctly after a match."""
        league = create_league()
        season = create_season(league)
        team1 = create_team(league)
        team2 = create_team(league)
        team_season1 = create_team_season(team1, season)
        team_season2 = create_team_season(team2, season)
        schedule = create_schedule(season)
        match_night = create_match_night(schedule)

        match = create_match(match_night, team_season1, team_season2)
        match.home_race_to = 15
        match.away_race_to = 12
        match.home_score = 15
        match.away_score = 10
        match.status = 'completed'

        match.save()

        match.refresh_from_db()
        self.assertEqual(match.winner, 'home')

        team_season1.refresh_from_db()
        self.assertEqual(team_season1.wins, 1)
        self.assertEqual(team_season1.games_won, 15)

        team_season2.refresh_from_db()
        self.assertEqual(team_season2.losses, 1)
        self.assertEqual(team_season2.games_lost, 10)

    def test_team_snapshot_recorded(self):
        """Test that team snapshot is correctly recorded after a match."""
        league = create_league()
        season = create_season(league)
        team1 = create_team(league)
        team2 = create_team(league)
        team_season1 = create_team_season(team1, season)
        team_season2 = create_team_season(team2, season)
        schedule = create_schedule(season)
        match_night = create_match_night(schedule)

        match = create_match(match_night, team_season1, team_season2)

        team_season1.wins = 5
        team_season1.losses = 2
        team_season1.games_won = 30
        team_season1.games_lost = 15
        team_season1.save()

        team_season2.wins = 6
        team_season2.losses = 1
        team_season2.games_won = 35
        team_season2.games_lost = 10
        team_season2.save()

        match.home_race_to = 15
        match.away_race_to = 12
        match.home_score = 15
        match.away_score = 10
        match.status = 'completed'
        match.save()

        match.refresh_from_db()
        self.assertIsNotNone(match.team_snapshot)

        self.assertEqual(
            match.team_snapshot['home_team']['team_name'], team1.name)
        self.assertEqual(match.team_snapshot['home_team']['wins'], 5)
        self.assertEqual(match.team_snapshot['home_team']['losses'], 2)
        self.assertEqual(match.team_snapshot['home_team']['games_won'], 30)
        self.assertEqual(match.team_snapshot['home_team']['games_lost'], 15)

        self.assertEqual(
            match.team_snapshot['away_team']['team_name'], team2.name)
        self.assertEqual(match.team_snapshot['away_team']['wins'], 6)
        self.assertEqual(match.team_snapshot['away_team']['losses'], 1)
        self.assertEqual(match.team_snapshot['away_team']['games_won'], 35)
        self.assertEqual(match.team_snapshot['away_team']['games_lost'], 10)


class GameModelTests(TestCase):
    """Test Game model functionality."""

    def setUp(self):
        """Set up required objects for testing."""
        league = create_league()
        season = create_season(league)
        self.team1 = create_team(league)
        self.team2 = create_team(league)
        self.team_season1 = create_team_season(self.team1, season)
        self.team_season2 = create_team_season(self.team2, season)
        schedule = create_schedule(season)
        self.match_night = create_match_night(schedule)
        self.match = create_match(
            self.match_night, self.team_season1, self.team_season2)
        self.home_player = create_team_player(self.team_season1)
        self.away_player = create_team_player(self.team_season2)

    def test_create_game(self):
        """Test creating a game and setting basic fields."""
        game = create_game(self.match, self.home_player,
                           self.away_player, home_score=5, away_score=3)

        self.assertEqual(game.match, self.match)
        self.assertEqual(game.home_player, self.home_player)
        self.assertEqual(game.away_player, self.away_player)
        self.assertEqual(game.home_score, 5)
        self.assertEqual(game.away_score, 3)
        self.assertEqual(game.status, 'completed')

    def test_update_game_winner(self):
        """Test updating the game winner based on scores."""
        game = create_game(
            self.match,
            self.home_player,
            self.away_player,
            home_score=7,
            away_score=5,
            home_race_to=7,
            away_race_to=7
        )

        game.save()

        game.refresh_from_db()
        self.assertEqual(game.winner, 'home')
        self.match.refresh_from_db()
        self.assertEqual(self.match.home_score, 1)

    def test_set_player_snapshot(self):
        """Test that the player snapshot is set
        correctly when the game is completed."""
        game = create_game(self.match, self.home_player,
                           self.away_player, home_score=7, away_score=5)

        game.save()

        self.assertIn('home_player', game.player_snapshot)
        self.assertIn('away_player', game.player_snapshot)
        self.assertEqual(
            game.player_snapshot['home_player']['player_name'],
            self.home_player.player.name)
        self.assertEqual(
            game.player_snapshot['away_player']['player_name'],
            self.away_player.player.name)

    def test_default_race_to_value(self):
        """Test that the default race-to value is set to 1 if not provided."""
        game = create_game(self.match, self.home_player, self.away_player)

        game.save()

        game.refresh_from_db()
        self.assertEqual(game.home_race_to, 1)
        self.assertEqual(game.away_race_to, 1)
