"""
Tests team API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Team,
    League,
    Player,
    Season,
    TeamPlayer,
    TeamSeason,
)
from team.serializers import TeamSerializer
from core.tests.test_models import random_string, create_admin


def team_player_detail_url(
        league_id, season_id, team_season_id, team_player_id):
    """Return team player detail URL"""
    return reverse(
        'league:teamplayer-detail',
        args=[league_id, season_id, team_season_id, team_player_id]
    )


def team_detail_url(league_id, team_id):
    """Return team detail URL"""
    return reverse('league:team-detail', args=[league_id, team_id])


def team_player_list_url(league_id, season_id, team_season_id):
    """Return team player list URL"""
    return reverse(
        'league:teamplayer-list',
        args=[league_id, season_id, team_season_id]
    )


def teams_list_url(league_id):
    """Return teams list URL"""
    return reverse('league:team-list', args=[league_id])


def create_league(admin_user, **params):
    """Create and return a sample league"""
    defaults = {
        'name': random_string(),
        'is_active': True,
    }
    defaults.update(params)

    return League.objects.create(admin=admin_user, **defaults)


def create_player(**params):
    """Create and return a sample player"""
    defaults = {
        'name': random_string(),
    }
    defaults.update(params)

    return Player.objects.create(**defaults)


def create_season(league, **params):
    """Create and return a sample season"""
    defaults = {
        'name': random_string(),
        'year': 2021,
        'league': league,
    }
    defaults.update(params)

    return Season.objects.create(**defaults)


def create_team(league, **params):
    """Create and return a sample team"""
    defaults = {
        'name': random_string(),
        'league': league,
    }
    defaults.update(params)

    return Team.objects.create(**defaults)


def create_team_season(team, season, **params):
    """Create and return a sample TeamSeason"""
    defaults = {
        'team': team,
        'season': season,
        'captain': create_player(),
    }
    defaults.update(params)

    return TeamSeason.objects.create(**defaults)


def create_team_player(team_season, player, **params):
    """Create and return a sample TeamPlayer"""
    defaults = {
        'team_season': team_season,
        'player': player,
        'handicap': 3,
    }
    defaults.update(params)

    return TeamPlayer.objects.create(**defaults)


class PublicTeamApiTests(TestCase):
    """Test unauthenticated team API access"""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(create_admin())

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(teams_list_url(self.league.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_team_detail_unauthorized(self):
        """Test that authentication is required to get team detail"""
        league = create_league(create_admin())
        team = create_team(league)
        url = team_detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_team_unauthorized(self):
        """Test that authentication is required to create a team"""
        league = create_league(create_admin())
        payload = {
            'name': random_string(),
            'league': league.id,
            'year': 2021,
            'is_active': True,
        }
        res = self.client.post(teams_list_url(self.league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicTeamPlayerApiTests(TestCase):
    """Test unauthenticated team API access"""

    def setUp(self):
        self.client = APIClient()
        self.league = create_league(create_admin())
        self.season = create_season(self.league)
        self.team = create_team(self.league)
        self.team_season = create_team_season(
            self.team, self.season, captain=create_player())
        self.player = create_player()
        self.team_player = create_team_player(self.team_season, self.player)

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_team_player_detail_unauthorized(self):
        """Test that authentication is required to get team player detail"""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_team_player_unauthorized(self):
        """Test that authentication is required to create a team player"""
        payload = {
            'player': self.player.id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }
        res = self.client.post(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_team_player_unauthorized(self):
        """Test that authentication is required to update a team player"""
        payload = {
            'handicap': 4,
        }
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_team_player_unauthorized(self):
        """Test that authentication is required to delete a team player"""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminTeamApiTests(TestCase):
    """Test authenticated team API access"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_admin_user = get_user_model().objects.create_user(
            'otheradmin@example.com',
            'test123',
            is_admin=True,
        )
        self.league = create_league(self.admin_user)
        self.client.force_authenticate(self.admin_user)

    def test_create_team_successful(self):
        """Test creating a new team"""
        league = create_league(self.admin_user)
        payload = {
            'name': random_string(),
            'league': league.id,
            'captain': create_player().id,
        }
        res = self.client.post(teams_list_url(league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team = Team.objects.get(id=res.data['id'])
        self.assertEqual(payload['name'], team.name)
        self.assertEqual(payload['league'], team.league.id)

    def test_retrieve_teams(self):
        """Test retrieving a list of teams"""
        league = create_league(self.admin_user)
        create_team(league)
        create_team(league)

        res = self.client.get(teams_list_url(league.id))

        teams = Team.objects.all().order_by('name')
        serializer = TeamSerializer(teams, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_team_has_players(self):
        """Test retrieving a team that has players."""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        player = create_player()
        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())

        create_team_player(team_season, player)

        url = team_detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(
            player.name,
            [p['name'] for season in res.data['team_season']
                for p in season['team_players']]
        )

    def test_create_team_invalid(self):
        """Test creating a team with invalid payload fails."""
        league = create_league(self.admin_user)

        payload = {
            'name': '',
            'league': league.id,
            'captain': '',
        }
        res = self.client.post(teams_list_url(self.league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['name'][0].code, 'blank')

    def test_get_team_detail(self):
        """Test retrieving a team detail as an authenticated user."""
        league = create_league(self.admin_user)
        team = create_team(league)
        url = team_detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data['name'], team.name)
        self.assertEqual(res.data['league'], team.league.id)

    def test_update_team(self):
        """Test updating a team as admin."""
        league = create_league(self.admin_user)
        team = create_team(league)
        payload = {
            'name': random_string(),
            'league': league.id,
        }
        url = team_detail_url(league.id, team.id)
        res = self.client.put(url, payload)

        team.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(team.name, payload['name'])
        self.assertEqual(team.league.id, payload['league'])

    def test_partial_update_team(self):
        """Test updating a team with patch."""
        league = create_league(self.admin_user)
        team = create_team(league)
        payload = {
            'name': random_string(),
        }
        url = team_detail_url(league.id, team.id)
        res = self.client.patch(url, payload)

        team.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(team.name, payload['name'])

    def test_delete_team(self):
        """Test deleting a team."""
        league = create_league(self.admin_user)
        team = create_team(league)
        url = team_detail_url(league.id, team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.filter(id=team.id).count(), 0)

    def test_admin_cannot_create_team_for_other_league(self):
        """Test that admin cannot create a team for another league"""
        league = create_league(self.other_admin_user)
        payload = {
            'name': random_string(),
            'league': league.id,
            'captain': create_player().id,
        }
        res = self.client.post(teams_list_url(league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_update_team_for_other_league(self):
        """Test that admin cannot update a team for another league"""
        league = create_league(self.other_admin_user)
        team = create_team(league)
        payload = {
            'name': random_string(),
            'league': league.id,
            'captain': create_player().id,
        }
        url = team_detail_url(league.id, team.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_delete_team_for_other_league(self):
        """Test that admin cannot delete a team for another league"""
        league = create_league(self.other_admin_user)
        team = create_team(league)
        url = team_detail_url(league.id, team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTeamPlayerApiTests(TestCase):
    """Test authenticated team API access"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_admin_user = get_user_model().objects.create_user(
            'otheradmin@example.com',
            'test123',
            is_admin=True,
        )
        self.league = create_league(self.admin_user)
        self.client.force_authenticate(self.admin_user)
        self.season = create_season(self.league)
        self.team = create_team(self.league)
        self.team_season = create_team_season(
            self.team, self.season, captain=create_player())
        self.player = create_player()
        self.team_player = create_team_player(self.team_season, self.player)

    def test_create_team_player_successful(self):
        """Test creating a new team player"""
        newPlayer = create_player(name='Player 1')
        payload = {
            'player': newPlayer.id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }
        res = self.client.post(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(payload['player'], team_player.player.id)
        self.assertEqual(payload['handicap'], team_player.handicap)
        self.assertEqual(payload['wins'], team_player.wins)
        self.assertEqual(payload['losses'], team_player.losses)
        self.assertEqual(payload['is_active'], team_player.is_active)

    def test_retrieve_team_players(self):
        """Test retrieving a list of team players"""
        create_team_player(self.team_season, create_player())
        create_team_player(self.team_season, create_player())

        res = self.client.get(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id))

        team_players = TeamPlayer.objects.all().order_by('player__name')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 4)
        self.assertEqual(len(res.data), team_players.count())

    def test_team_player_has_player(self):
        """Test retrieving a team player that has a player."""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['player'], self.player.id)

    def test_create_team_player_invalid(self):
        """Test creating a team player with invalid payload fails."""
        payload = {
            'player': '',
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }
        res = self.client.post(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['player'][0].code, 'null')

    def test_get_team_player_detail(self):
        """Test retrieving a team player detail as an authenticated user."""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['player'], self.player.id)
        self.assertEqual(res.data['handicap'], self.team_player.handicap)
        self.assertEqual(res.data['wins'], self.team_player.wins)
        self.assertEqual(res.data['losses'], self.team_player.losses)
        self.assertEqual(res.data['is_active'], self.team_player.is_active)

    def test_update_team_player(self):
        """Test updating a team player as admin."""
        payload = {
            'player': self.player.id,
            'handicap': 4,
        }
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.put(url, payload)

        self.team_player.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.team_player.handicap, payload['handicap'])

    def test_partial_update_team_player(self):
        """Test updating a team player with patch."""
        payload = {
            'handicap': 4,
        }
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.patch(url, payload)

        self.team_player.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.team_player.handicap, payload['handicap'])

    def test_delete_team_player(self):
        """Test deleting a team player."""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            TeamPlayer.objects.filter(id=self.team_player.id).count(), 0)

    def test_admin_cannot_create_team_player_for_other_league(self):
        """Test that admin cannot create a team player for another league"""
        league = create_league(self.other_admin_user)
        payload = {
            'player': create_player().id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }
        res = self.client.post(team_player_list_url(
            league.id, self.season.id, self.team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_update_team_player_for_other_league(self):
        """Test that admin cannot update a team player for another league"""
        league = create_league(self.other_admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.season)
        team_player = create_team_player(team_season, create_player())
        payload = {
            'handicap': 4,
        }
        url = team_player_detail_url(
            league.id,
            self.season.id,
            team_season.id,
            team_player.id
        )
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_delete_team_player_for_other_league(self):
        """Test that admin cannot delete a team player for another league"""
        league = create_league(self.other_admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.season)
        team_player = create_team_player(team_season, create_player())
        url = team_player_detail_url(
            league.id,
            self.season.id,
            team_season.id,
            team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_captain_auto_added_as_team_player(self):
        """Test that the captain is automatically added as a team player."""
        team = create_team(self.league)
        season = create_season(self.league)
        player = create_player()
        team_season = create_team_season(team, season, captain=player)

        self.client.force_authenticate(self.admin_user)
        url = team_player_list_url(self.league.id, season.id, team_season.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['player'], player.id)

    def test_player_switch_teams_sets_previous_inactive(self):
        """Test that when a player switches teams,
        their previous team_player is set to inactive."""
        team1 = create_team(self.league)
        team2 = create_team(self.league)
        season = create_season(self.league)
        player = create_player()

        team_season1 = create_team_season(
            team1, season, captain=create_player())
        team_player1 = create_team_player(team_season1, player)

        self.assertTrue(team_player1.is_active)

        team_season2 = create_team_season(
            team2, season, captain=create_player())
        payload = {
            'player': player.id,
        }
        res = self.client.post(
            team_player_list_url(self.league.id, season.id, team_season2.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        team_player1.refresh_from_db()

        self.assertFalse(team_player1.is_active)

        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertTrue(new_team_player.is_active)

    def test_player_record_preserved_on_team_change(self):
        """Test that a player's record is preserved when they change teams."""
        team1 = create_team(self.league)
        team2 = create_team(self.league)
        season = create_season(self.league)
        player = create_player()

        team_season1 = create_team_season(
            team1, season, captain=create_player())
        team_player1 = create_team_player(
            team_season1,
            player,
            handicap=7,
            wins=5,
            losses=10,
            racks_won=25,
            racks_lost=30
        )

        self.assertEqual(team_player1.wins, 5)
        self.assertEqual(team_player1.losses, 10)
        self.assertEqual(team_player1.racks_won, 25)
        self.assertEqual(team_player1.racks_lost, 30)
        self.assertEqual(team_player1.handicap, 7)

        team_season2 = create_team_season(
            team2, season, captain=create_player())
        payload = {
            'player': player.id,
        }
        res = self.client.post(
            team_player_list_url(self.league.id, season.id, team_season2.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team_player1.refresh_from_db()

        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertFalse(team_player1.is_active)
        self.assertEqual(new_team_player.wins, 5)
        self.assertEqual(new_team_player.losses, 10)
        self.assertEqual(new_team_player.racks_won, 25)
        self.assertEqual(new_team_player.racks_lost, 30)
        self.assertEqual(team_player1.handicap, 7)

    def test_player_retains_rating_in_new_season(self):
        """Test that a player retains their rating in a new season."""
        team = create_team(self.league)
        season = create_season(self.league)
        player = create_player()

        team_season = create_team_season(
            team, season, captain=create_player())
        create_team_player(
            team_season,
            player,
            handicap=7,
            wins=5,
            losses=10,
            racks_won=25,
            racks_lost=30
        )

        new_season = create_season(self.league, year=2022)
        new_team_season = create_team_season(
            team, new_season, captain=create_player())

        payload = {
            'player': player.id,
        }
        res = self.client.post(
            team_player_list_url(
                self.league.id, new_season.id, new_team_season.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(new_team_player.handicap, 7)
        self.assertEqual(new_team_player.wins, 0)
        self.assertEqual(new_team_player.losses, 0)
        self.assertEqual(new_team_player.racks_won, 0)
        self.assertEqual(new_team_player.racks_lost, 0)

    def test_player_retains_latest_rating_across_seasons(self):
        """Test that a player retains the
        latest handicap when starting a new season."""
        team = create_team(self.league)
        player = create_player()

        season1 = create_season(self.league, year=2020)
        team_season1 = create_team_season(
            team, season1, captain=create_player())
        create_team_player(team_season1, player, handicap=5)

        season2 = create_season(self.league, year=2021)
        team_season2 = create_team_season(
            team, season2, captain=create_player())
        team_player2 = create_team_player(team_season2, player)

        payload = {'handicap': 8}
        url = team_player_detail_url(
            self.league.id, season2.id, team_season2.id, team_player2.id)
        self.client.patch(url, payload)

        season3 = create_season(self.league, year=2022)
        team_season3 = create_team_season(
            team, season3, captain=create_player())

        payload = {'player': player.id}
        res = self.client.post(
            team_player_list_url(self.league.id, season3.id, team_season3.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(new_team_player.handicap, 8)

    def test_overwrite_rating_across_seasons(self):
        """Test that a player retains the latest
        handicap when starting a new season."""
        team = create_team(self.league)
        player = create_player()

        season1 = create_season(self.league, year=2020)
        team_season1 = create_team_season(
            team, season1, captain=create_player())
        create_team_player(team_season1, player, handicap=5)

        season2 = create_season(self.league, year=2021)
        team_season2 = create_team_season(
            team, season2, captain=create_player())
        team_player2 = create_team_player(team_season2, player)

        payload = {'handicap': 8}
        url = team_player_detail_url(
            self.league.id, season2.id, team_season2.id, team_player2.id)
        self.client.patch(url, payload)

        season3 = create_season(self.league, year=2022)
        team_season3 = create_team_season(
            team, season3, captain=create_player())

        payload = {'player': player.id, 'handicap': 6}
        res = self.client.post(
            team_player_list_url(self.league.id, season3.id, team_season3.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(new_team_player.handicap, 6)

    def test_player_association_with_correct_team_and_season(self):
        """Test that the new TeamPlayer entry
        corresponds to the correct team and player."""
        team1 = create_team(self.league)
        team2 = create_team(self.league)
        player = create_player()

        season = create_season(self.league)
        team_season1 = create_team_season(
            team1, season, captain=create_player())
        create_team_player(team_season1, player, handicap=7)

        new_season = create_season(self.league, year=2022)
        new_team_season = create_team_season(
            team2, new_season, captain=create_player())

        payload = {'player': player.id}
        res = self.client.post(
            team_player_list_url(
                self.league.id, new_season.id, new_team_season.id),
            payload
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(new_team_player.player, player)
        self.assertEqual(new_team_player.team_season, new_team_season)
        self.assertEqual(new_team_player.handicap, 7)


class AdditionAdminLeagueApiTests(TestCase):
    """Test authenticated team API access"""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.additional_admin_user = get_user_model().objects.create_user(
            'additionaladmin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_user = get_user_model().objects.create_user(
            'user@example.com',
            'test123',
            is_admin=False,
        )
        player_profile = create_player(name='Player 1')
        self.other_user.player_profile = player_profile
        self.other_user.save()

        self.league = create_league(self.admin_user)
        self.team = create_team(self.league)

        self.client.force_authenticate(self.admin_user)

    def test_additional_admin_can_create_team(self):
        """Test that additional admin can create a team"""
        league = create_league(self.admin_user)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'name': random_string(),
            'league': league.id,
        }

        res = self.client.post(teams_list_url(league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team = Team.objects.get(id=res.data['id'])
        self.assertEqual(payload['name'], team.name)
        self.assertEqual(payload['league'], team.league.id)

    def test_additional_admin_can_update_team(self):
        """Test that additional admin can update a team"""
        league = create_league(self.admin_user)
        team = create_team(league)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'name': random_string(),
            'league': league.id,
        }
        url = team_detail_url(league.id, team.id)
        res = self.client.put(url, payload)

        team.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(team.name, payload['name'])
        self.assertEqual(team.league.id, payload['league'])

    def test_additional_admin_can_delete_team(self):
        """Test that additional admin can delete a team"""
        league = create_league(self.admin_user)
        team = create_team(league)
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        url = team_detail_url(league.id, team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.filter(id=team.id).count(), 0)

    def test_user_cannot_create_team(self):
        """Test that a user cannot create a team"""
        league = create_league(self.admin_user)

        self.client.force_authenticate(self.other_user)

        payload = {
            'name': random_string(),
            'league': league.id,
            'captain': create_player().id,
        }

        res = self.client.post(teams_list_url(league.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_team(self):
        """Test that a user cannot update a team"""
        league = create_league(self.admin_user)

        payload = {
            'name': random_string(),
            'league': league.id,
        }

        self.client.force_authenticate(self.other_user)
        url = team_detail_url(league.id, self.team.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_team(self):
        """Test that a user cannot delete a team"""
        league = create_league(self.admin_user)
        create_team(league)

        self.client.force_authenticate(self.other_user)

        url = team_detail_url(league.id, self.team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_retrieve_teams(self):
        """Test that a user can retrieve a list of teams in their league."""
        self.other_user.player_profile.teams.clear()

        league = create_league(self.admin_user)
        team1 = create_team(league)
        team2 = create_team(league)

        season = create_season(league)
        team_season1 = TeamSeason.objects.create(
            team=team1, season=season, captain=create_player())
        TeamSeason.objects.create(
            team=team2, season=season, captain=create_player())

        create_team_player(team_season1, self.other_user.player_profile)

        self.client.force_authenticate(self.other_user)

        res = self.client.get(teams_list_url(league.id))

        teams = Team.objects.filter(league=league).order_by('name')
        serializer = TeamSerializer(teams, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_user_can_get_team_detail(self):
        """Test that a user can retrieve a team detail."""
        self.other_user.player_profile.teams.clear()

        league = create_league(self.admin_user)
        team = create_team(league)
        season = create_season(league)
        team_season = TeamSeason.objects.create(
            team=team, season=season, captain=create_player())
        create_team_player(team_season, self.other_user.player_profile)

        self.client.force_authenticate(self.other_user)

        url = team_detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data['name'], team.name)
        self.assertEqual(res.data['league'], team.league.id)


class AdditionAdminTeamPlayerApiTests(TestCase):
    """Test authenticated team API access"""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            'admin4@admin.com',
            'test123',
            is_admin=True,
        )
        self.additional_admin_user = get_user_model().objects.create_user(
            'admin5@admin.com',
            'test123',
            is_admin=True,
        )
        self.other_user = get_user_model().objects.create_user(
            'user3@user.com',
            'test123',
            is_admin=False,
        )
        player_profile = create_player(name='Player 1')
        self.other_user.player_profile = player_profile
        self.other_user.save()

        self.league = create_league(self.admin_user)
        self.season = create_season(self.league)
        self.league.additional_admins.add(self.additional_admin_user)
        self.team = create_team(self.league)

        self.client.force_authenticate(self.additional_admin_user)

    def test_additional_admin_can_create_team_player(self):
        """Test that additional admin can create a team player"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'player': create_player().id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }

        res = self.client.post(team_player_list_url(
            league.id, season.id, team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        team_player = TeamPlayer.objects.get(id=res.data['id'])
        self.assertEqual(payload['player'], team_player.player.id)
        self.assertEqual(payload['handicap'], team_player.handicap)
        self.assertEqual(payload['wins'], team_player.wins)
        self.assertEqual(payload['losses'], team_player.losses)
        self.assertEqual(payload['is_active'], team_player.is_active)

    def test_additional_admin_can_update_team_player(self):
        """Test that additional admin can update a team player"""
        league = create_league(self.admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.league.seasons.first())
        team_player = create_team_player(team_season, create_player())
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'player': create_player().id,
            'handicap': 4,
        }
        url = team_player_detail_url(
            league.id,
            self.league.seasons.first().id,
            team_season.id,
            team_player.id
        )
        res = self.client.put(url, payload)

        team_player.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(team_player.handicap, payload['handicap'])

    def test_additional_admin_can_delete_team_player(self):
        """Test that additional admin can delete a team player"""
        league = create_league(self.admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.league.seasons.first())
        team_player = create_team_player(team_season, create_player())
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        url = team_player_detail_url(
            league.id,
            self.league.seasons.first().id,
            team_season.id,
            team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            TeamPlayer.objects.filter(id=team_player.id).count(), 0)

    def test_additional_admin_can_fetch_team_players(self):
        """Test that additional admin can fetch team players"""
        league = create_league(self.admin_user)
        team = create_team(league)
        season = create_season(league)
        team_season = create_team_season(team, season, captain=create_player())
        create_team_player(team_season, create_player())
        league.additional_admins.add(self.additional_admin_user)

        self.client.force_authenticate(self.additional_admin_user)

        res = self.client.get(team_player_list_url(
            league.id, season.id, team_season.id))

        team_players = TeamPlayer.objects.all().order_by('player__name')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(len(res.data), team_players.count())

    def test_additional_admin_cannot_create_team_player_for_other_league(self):
        """Test that additional admin cannot
        create a team player for another league"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'player': create_player().id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }

        res = self.client.post(team_player_list_url(
            league.id, season.id, team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_additional_admin_cannot_update_team_player_for_other_league(self):
        """Test that additional admin cannot
        update a team player for another league"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season)
        team_player = create_team_player(team_season, create_player())

        self.client.force_authenticate(self.additional_admin_user)

        payload = {
            'handicap': 4,
        }
        url = team_player_detail_url(
            league.id,
            season.id,
            team_season.id,
            team_player.id
        )
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_additional_admin_cannot_delete_team_player_for_other_league(self):
        """Test that additional admin cannot
        delete a team player for another league"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season)
        team_player = create_team_player(team_season, create_player())

        self.client.force_authenticate(self.additional_admin_user)

        url = team_player_detail_url(
            league.id,
            season.id,
            team_season.id,
            team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class UserTeamPlayerApiTests(TestCase):
    """Test authenticated team API access"""

    def setUp(self):
        self.client = APIClient()

        self.admin_user = get_user_model().objects.create_user(
            'admin@example.com',
            'test123',
            is_admin=True,
        )
        self.other_user = get_user_model().objects.create_user(
            'user@example.com',
            'test123',
            is_admin=False,
        )

        player_profile = create_player(name='Player 1')
        self.other_user.player_profile = player_profile
        self.other_user.save()

        self.league = create_league(self.admin_user)
        self.season = create_season(self.league)
        self.team = create_team(self.league)
        self.team_season = create_team_season(
            self.team, self.season, captain=create_player())
        self.team_player = create_team_player(self.team_season, player_profile)

        self.client.force_authenticate(self.other_user)

    def test_user_cannot_create_team_player(self):
        """Test that a user cannot create a team player"""
        league = create_league(self.admin_user)
        season = create_season(league)
        team = create_team(league)
        team_season = create_team_season(team, season, captain=create_player())

        payload = {
            'player': create_player().id,
            'handicap': 3,
            'wins': 0,
            'losses': 0,
            'is_active': True,
        }

        res = self.client.post(team_player_list_url(
            league.id, season.id, team_season.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_team_player(self):
        """Test that a user cannot update a team player"""
        league = create_league(self.admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.league.seasons.first())
        team_player = create_team_player(team_season, create_player())

        payload = {
            'player': create_player().id,
            'handicap': 4,
        }
        url = team_player_detail_url(
            league.id,
            self.league.seasons.first().id,
            team_season.id,
            team_player.id
        )
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_team_player(self):
        """Test that a user cannot delete a team player"""
        league = create_league(self.admin_user)
        team = create_team(league)
        team_season = create_team_season(team, self.league.seasons.first())
        team_player = create_team_player(team_season, create_player())

        url = team_player_detail_url(
            league.id,
            self.league.seasons.first().id,
            team_season.id,
            team_player.id
        )
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_fetch_team_players_in_their_league(self):
        """Test that a user associated with
        a league can fetch its team players"""
        res = self.client.get(team_player_list_url(
            self.league.id, self.season.id, self.team_season.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[1]['player'],
                         self.other_user.player_profile.id)
        self.assertEqual(res.data[0]['player'], self.team_season.captain.id)

    def test_user_can_get_team_player_detail(self):
        """Test that a user can retrieve a team player detail."""
        url = team_player_detail_url(
            self.league.id,
            self.season.id,
            self.team_season.id,
            self.team_player.id
        )
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['player'], self.other_user.player_profile.id)
        self.assertEqual(res.data['handicap'], self.team_player.handicap)
        self.assertEqual(res.data['wins'], self.team_player.wins)
        self.assertEqual(res.data['losses'], self.team_player.losses)
        self.assertEqual(res.data['is_active'], self.team_player.is_active)
