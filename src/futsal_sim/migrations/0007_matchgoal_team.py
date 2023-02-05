# Generated by Django 4.1.3 on 2023-02-04 23:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futsal_sim', '0006_player_stamina_left'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchgoal',
            name='team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='goal_moments', to='futsal_sim.team'),
            preserve_default=False,
        ),
    ]
