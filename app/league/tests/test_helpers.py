from core.models import League, Season, Team, Player, TeamSeason, TeamPlayer
from core.tests.test_models import random_string


def create_league(admin_user, **params):
    """Helper function to create a league with the provided admin user."""
    defaults = {'name': random_string(), 'is_active': True}
    defaults.update(params)
    return League.objects.create(admin=admin_user, **defaults)


def create_season(league, **params):
    """Helper function to create a season."""
    defaults = {'name': random_string(), 'league': league, 'year': 2021}
    defaults.update(params)
    return Season.objects.create(**defaults)


def create_team(league, **params):
    """Helper function to create a team."""
    defaults = {'name': random_string(), 'league': league}
    defaults.update(params)
    return Team.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Helper function to create a team season."""
    defaults = {'team': team, 'season': season, 'captain': create_player()}
    defaults.update(params)
    return TeamSeason.objects.create(**defaults)


def create_player(**params):
    """Helper function to create a player."""
    defaults = {'name': random_string()}
    defaults.update(params)
    return Player.objects.create(**defaults)


def create_team_player(team_season, player, **params):
    """Helper function to create a team player."""
    defaults = {'team_season': team_season, 'player': player}
    defaults.update(params)
    return TeamPlayer.objects.create(**defaults)
