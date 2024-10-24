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


def detail_url(league_id, team_id):
    """Return team detail URL"""
    return reverse('league:team-detail', args=[league_id, team_id])


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
        url = detail_url(league.id, team.id)
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
            team=team, season=season, captain=player)

        create_team_player(team_season, player)

        url = detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(player.name, [p['player']['name']
                      for p in res.data['team_season']['team_players']])

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
        url = detail_url(league.id, team.id)
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
        url = detail_url(league.id, team.id)
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
        url = detail_url(league.id, team.id)
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
        url = detail_url(league.id, team.id)
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
        url = detail_url(league.id, team.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_delete_team_for_other_league(self):
        """Test that admin cannot delete a team for another league"""
        league = create_league(self.other_admin_user)
        team = create_team(league)
        url = detail_url(league.id, team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


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
        url = detail_url(league.id, team.id)
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

        url = detail_url(league.id, team.id)
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
        url = detail_url(league.id, self.team.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_team(self):
        """Test that a user cannot delete a team"""
        league = create_league(self.admin_user)
        create_team(league)

        self.client.force_authenticate(self.other_user)

        url = detail_url(league.id, self.team.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_retrieve_teams(self):
        """Test that a user can retrieve a list of teams in their league."""
        self.other_user.player_profile.teams.clear()

        league = create_league(self.admin_user)
        team1 = create_team(league)
        team2 = create_team(league)

        season = create_season(league)
        team_season1 = TeamSeason.objects.create(
            team=team1, season=season, captain=self.other_user.player_profile)
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
            team=team, season=season, captain=self.other_user.player_profile)
        create_team_player(team_season, self.other_user.player_profile)

        self.client.force_authenticate(self.other_user)

        url = detail_url(league.id, team.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = TeamSerializer(team)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data['name'], team.name)
        self.assertEqual(res.data['league'], team.league.id)
