# Generated by Django 4.1.3 on 2023-01-18 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futsal_sim', '0002_remove_matchresult_cpu_average_skill_and_more'),
        ('users', '0002_user_active_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='active_team',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='active_team_of', to='futsal_sim.team'),
        ),
    ]