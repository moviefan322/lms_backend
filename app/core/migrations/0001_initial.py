# Generated by Django 4.0.10 on 2024-10-24 12:12

import core.models
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('handicap_range', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=5), default=core.models.default_handicap_range, size=None)),
                ('is_active', models.BooleanField(default=True)),
                ('additional_admins', models.ManyToManyField(blank=True, related_name='leagues_with_admin_privileges', to=settings.AUTH_USER_MODEL)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leagues_administered', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('year', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasons', to='core.league')),
            ],
            options={
                'unique_together': {('name', 'year', 'league')},
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='core.league')),
            ],
        ),
        migrations.CreateModel(
            name='TeamSeason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('games_won', models.IntegerField(default=0)),
                ('games_lost', models.IntegerField(default=0)),
                ('captain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teams_captained', to='core.player')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.team')),
            ],
            options={
                'unique_together': {('team', 'season')},
            },
        ),
        migrations.CreateModel(
            name='TeamPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handicap', models.IntegerField(default=3)),
                ('wins', models.IntegerField(default=0)),
                ('losses', models.IntegerField(default=0)),
                ('is_captain', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_players', to='core.player')),
                ('team_season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_players', to='core.teamseason')),
            ],
            options={
                'unique_together': {('team_season', 'player')},
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('num_weeks', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('default_start_time', models.TimeField(default='19:00')),
                ('season', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='core.season')),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='teams',
            field=models.ManyToManyField(blank=True, related_name='players', through='core.TeamPlayer', to='core.teamseason'),
        ),
        migrations.CreateModel(
            name='MatchNight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(default='Scheduled', max_length=50)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='match_nights', to='core.schedule')),
            ],
            options={
                'unique_together': {('date', 'schedule')},
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_time', models.TimeField()),
                ('home_score', models.IntegerField(blank=True, null=True)),
                ('away_score', models.IntegerField(blank=True, null=True)),
                ('home_race_to', models.IntegerField(blank=True, null=True)),
                ('away_race_to', models.IntegerField(blank=True, null=True)),
                ('winner', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.CharField(default='Scheduled', max_length=50)),
                ('team_snapshot', models.JSONField(blank=True, null=True)),
                ('lineups', models.JSONField(blank=True, null=True)),
                ('away_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matches', to='core.teamseason')),
                ('home_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matches', to='core.teamseason')),
                ('match_night', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='core.matchnight')),
            ],
            options={
                'unique_together': {('match_night', 'home_team', 'away_team')},
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_race_to', models.IntegerField(blank=True, null=True)),
                ('away_race_to', models.IntegerField(blank=True, null=True)),
                ('home_score', models.IntegerField(blank=True, null=True)),
                ('away_score', models.IntegerField(blank=True, null=True)),
                ('winner', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.CharField(default='Scheduled', max_length=50)),
                ('player_snapshot', models.JSONField(blank=True, null=True)),
                ('away_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_games', to='core.teamplayer')),
                ('home_player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_games', to='core.teamplayer')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='core.match')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='player_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to='core.player'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
