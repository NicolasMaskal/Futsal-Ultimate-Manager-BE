from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

from ..common.models import BaseModel
from ..users.models import User
from .constants import BASE_PRICE_FOR_AVERAGE_PLAYER, MAX_SQUAD_VALID_SIZE


class PlayerPosition(models.TextChoices):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


class Team(BaseModel):
    name = models.CharField(
        max_length=32, blank=False, null=False, validators=[MaxLengthValidator(32), MinLengthValidator(3)]
    )
    owner = models.ForeignKey(User, related_name="team", on_delete=models.CASCADE)
    wins = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    draws = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    loses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    coins = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    @property
    def has_valid_squad_size(self) -> bool:
        return self.players.count() <= MAX_SQUAD_VALID_SIZE


class Player(BaseModel):
    name = models.CharField(max_length=128)
    preferred_position = models.CharField(choices=PlayerPosition.choices, max_length=32)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="players")
    skill = models.IntegerField(validators=[MinValueValidator(1)])
    stamina_left = models.IntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(100)])

    matches_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_scored = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists_made = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    def is_gk(self) -> bool:
        return self.preferred_position == TeamSheet.goalkeeper

    def calc_sell_price(self, team_avg: int) -> int:
        sell_price = BASE_PRICE_FOR_AVERAGE_PLAYER - team_avg + self.skill
        return max(sell_price, 5)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_preferred_position_valid",
                check=models.Q(preferred_position__in=PlayerPosition.values),
            )
        ]


class TeamSheet(BaseModel):
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
    goalkeeper = models.ForeignKey(Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="goalkeeper")

    def __str__(self):
        return self.name


class MatchResult(BaseModel):
    date = models.DateTimeField(auto_now_add=True)
    player_team = models.ForeignKey(Team, related_name="team", on_delete=models.CASCADE)
    cpu_team_name = models.CharField(max_length=128)
    player_score = models.IntegerField(validators=[MinValueValidator(0)])
    cpu_score = models.IntegerField(validators=[MinValueValidator(0)])
    cpu_average_skill = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)])

    def __str__(self):
        return f"{self.player_score} : {self.cpu_score} ({self.cpu_average_skill})"
