# Generated by Django 4.0.10 on 2024-10-22 21:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_schedule_season'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='season',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='core.season'),
        ),
    ]