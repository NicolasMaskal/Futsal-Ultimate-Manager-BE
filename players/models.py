from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class PlayerPosition(models.TextChoices):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


class Team(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey("auth.User", related_name="team", on_delete=models.CASCADE)  # new

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=128)
    position = models.CharField(
        choices=PlayerPosition.choices, max_length=32
    )
    current_team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True)
    overall = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(99)]
    )

    def __str__(self):
        return self.name


class TeamSheet(models.Model):
    name = models.CharField(max_length=128)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PlayerTeamSheetLocation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, blank=True)
    index = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(4)])
    team_sheet = models.ForeignKey(TeamSheet, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player}: {self.index} ({self.team_sheet.name})"
