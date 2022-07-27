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
    preferred_position = models.CharField(choices=PlayerPosition.choices, max_length=32)
    current_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    overall = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    stamina_left = models.IntegerField(
        default=99, validators=[MinValueValidator(0), MaxValueValidator(99)]
    )

    matches_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_scored = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists_made = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class TeamSheet(models.Model):
    name = models.CharField(max_length=128)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    right_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_attacker"
    )
    left_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_attacker"
    )
    right_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_defender"
    )
    left_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_defender"
    )
    goalkeeper = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="goalkeeper"
    )

    def __str__(self):
        return self.name
