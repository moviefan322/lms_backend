# Generated by Django 4.0.10 on 2024-09-20 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_league_remove_player_team_team_player_teams'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
