from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.management import call_command
from core.models import (
    User,
    League,
    Season,
    Team,
    TeamSeason,
    Player,
    TeamPlayer,
)

from core.seed_data.team_seeds import (
    team_names,
    player_names,
    captain_names
    )


class Command(BaseCommand):
    help = 'Seed the league management database with teams, \
        players, seasons, matches, and games.'

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            # Flush the database
            self.stdout.write('Flushing the database...')
            call_command('flush', '--no-input')

            # Create a user
            admin = User.objects.create_user(
                email='admin@admin.com',
                password='admin',
                name='Test Admin',
                is_admin=True
            )

            # Create a league
            league = League.objects.create(name='Premier League', admin=admin)

            # Create a season
            season = Season.objects.create(
                name='2020/2021', year=2020, league=league)

            # Create teams
            for team_name in team_names:
                Team.objects.create(name=team_name, league=league)

            teams = Team.objects.all()

            # Create Players
            for player_name in player_names:
                Player.objects.create(name=player_name)

            players = Player.objects.all()

            # Create team seasons
            for index, team in enumerate(teams):
                captain = Player.objects.create(name=captain_names[index])
                TeamSeason.objects.create(
                    team=team, season=season, captain=captain)

            team_seasons = TeamSeason.objects.all()

            # Create team players and skip duplicates
            for index, player in enumerate(players):
                team_season = team_seasons[index % len(team_seasons)]
                if not TeamPlayer.objects.filter(
                        team_season=team_season, player=player).exists():
                    TeamPlayer.objects.create(
                        team_season=team_season, player=player)

            self.stdout.write(self.style.SUCCESS(
                'Database seeded successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error occurred: {e}"))
            raise
