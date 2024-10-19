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

team_names = [
    'Arsenal',
    'Aston Villa',
    'Bournemouth',
    'Burnley',
    'Chelsea',
    'Crystal Palace',
    'Everton',
    'Leicester City',
    'Liverpool',
    'Manchester City',
    'Manchester United',
    'Newcastle United',
    'Sheffield United',
    'Southampton',
    'Tottenham Hotspur',
    'West Ham United',
]

player_names = [
    'Pierre-Emerick Aubameyang',
    'Jack Grealish',
    'Callum Wilson',
    'Chris Wood',
    'Tammy Abraham',
    'Christian Pulisic',
    'Richarlison',
    'Jamie Vardy',
    'Mohamed Salah',
    'Raheem Sterling',
    'Marcus Rashford',
    'Allan Saint-Maximin',
    'John Lundstram',
    'Danny Ings',
    'Harry Kane',
    'Michail Antonio',
    'David Luiz',
    'Tyrone Mings',
    'Nathan Ake',
    'Ben Mee',
    'Kurt Zouma',
    'Gary Cahill',
    'Michael Keane',
    'Caglar Soyuncu',
    'Virgil van Dijk',
    'Aymeric Laporte',
    'Harry Maguire',
    'Federico Fernandez',
    'John Egan',
    'Jack O\'Connell',
    'Jan Bednarek',
    'James Ward-Prowse',
    'Harry Winks',
    'Declan Rice',
    'Granit Xhaka',
    'Douglas Luiz',
    'Mateo Kovacic',
    'Luka Milivojevic',
    'Andre Gomes',
    'Wilfred Ndidi',
    'Rodri',
    'Fred',
    'Jonjo Shelvey',
    'John Fleck',
    'Oriol Romeu',
    'Tangu Ndombele',
    'Mark Noble',
    'Kevin De Bruyne',
    'David Silva',
    'Bruno Fernandes',
    'Allan Saint-Maximin',
    'James Maddison',
    'Jordan Henderson',
    'James Ward-Prowse',
    'Mason Mount',
    'Wilfred Ndidi',
    'Declan Rice',
    'Mateo Kovacic',
    'Jonjo Shelvey',
    'John Fleck',
    'Jack Grealish',
    'David Silva',
    'Bruno Fernandes',
    'Raheem Sterling',
]


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
                email='testadmin@admin.com',
                password='testpass123',
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
                captain = players[index * 4]
                TeamSeason.objects.create(
                    team=team, season=season, captain=captain)

            team_seasons = TeamSeason.objects.all()

            # Create team players
            for index, player in enumerate(players):
                team_season = team_seasons[index % len(team_seasons)]
                TeamPlayer.objects.create(
                    team_season=team_season, player=player)

            self.stdout.write(self.style.SUCCESS(
                'Database seeded successfully!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error occurred: {e}"))
            raise
