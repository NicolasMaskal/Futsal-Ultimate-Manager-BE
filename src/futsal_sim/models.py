from typing import Optional

from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

from ..common.models import BaseModel
from ..users.models import User
from .constants import (
    BASE_PRICE_FOR_AVERAGE_PLAYER,
    MAX_SQUAD_VALID_SIZE,
    MIN_PLAYER_SKILL,
    PLAYER_AMOUNT_TEAM_SHEET,
)


class PlayerPosition(models.TextChoices):
    ATTACKER = "attacker"
    DEFENDER = "defender"
    GOALKEEPER = "goalkeeper"


class Team(BaseModel):
    name = models.CharField(
        max_length=32, blank=False, null=False, validators=[MaxLengthValidator(32), MinLengthValidator(3)]
    )
    # If null, is owned by AI
    owner = models.ForeignKey(User, related_name="teams", on_delete=models.CASCADE, null=True, default=None)
    wins = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    draws = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    loses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    coins = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    @property
    def has_valid_squad_size(self) -> bool:
        return PLAYER_AMOUNT_TEAM_SHEET <= self.players.count() <= MAX_SQUAD_VALID_SIZE

    @property
    def matches_played(self) -> int:
        return self.wins + self.draws + self.loses


class CPUTeam(Team):
    skill = models.IntegerField(validators=[MinValueValidator(MIN_PLAYER_SKILL)])

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_owner_valid",
                check=models.Q(owner__active_team__isnull=True),
            )
        ]


class Player(BaseModel):
    name = models.CharField(max_length=128)
    preferred_position = models.CharField(choices=PlayerPosition.choices, max_length=32)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name="players")
    skill = models.IntegerField(validators=[MinValueValidator(MIN_PLAYER_SKILL)])

    matches_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_scored = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists_made = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name

    def is_gk(self) -> bool:
        return self.preferred_position == TeamSheet.goalkeeper

    def calc_sell_price(self, team_avg: float) -> int:
        sell_price = BASE_PRICE_FOR_AVERAGE_PLAYER - team_avg + self.skill
        return max(round(sell_price), 5)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_preferred_position_valid",
                check=models.Q(preferred_position__in=PlayerPosition.values),
            )
        ]


class TeamPlayersInPositions(BaseModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    right_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_attacker_%(class)s"
    )
    left_attacker = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_attacker_%(class)s"
    )
    right_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="right_defender_%(class)s"
    )
    left_defender = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="left_defender_%(class)s"
    )
    goalkeeper = models.ForeignKey(
        Player, blank=True, null=True, on_delete=models.SET_NULL, related_name="goalkeeper_%(class)s"
    )

    @property
    def players(self) -> list[Optional[Player]]:
        return [self.right_attacker, self.left_attacker, self.right_defender, self.left_defender, self.goalkeeper]

    class Meta:
        abstract = True


class TeamSheet(TeamPlayersInPositions):
    name = models.CharField(max_length=128)

    @property
    def is_ready_for_match(self) -> bool:
        return None not in self.players


class TeamLineup(TeamPlayersInPositions):
    pass


class MatchResult(BaseModel):
    date = models.DateTimeField(auto_now_add=True)
    player_team = models.ForeignKey(Team, related_name="player_team", on_delete=models.CASCADE)
    cpu_team = models.ForeignKey(Team, related_name="cpu_team", on_delete=models.CASCADE)
    player_lineup = models.ForeignKey(TeamLineup, related_name="matches_as_player", on_delete=models.CASCADE)
    cpu_lineup = models.ForeignKey(TeamLineup, related_name="matches_as_cpu", on_delete=models.CASCADE)
    player_goals = models.IntegerField(validators=[MinValueValidator(0)])
    cpu_goals = models.IntegerField(validators=[MinValueValidator(0)])
    coins_reward = models.IntegerField(validators=[MinValueValidator(0)])


class MatchGoal(BaseModel):
    minute = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(40)])
    goal_scorer = models.ForeignKey(Player, related_name="goal_moments", on_delete=models.CASCADE)
    assister = models.ForeignKey(Player, related_name="assist_moments", on_delete=models.CASCADE, null=True)
    match = models.ForeignKey(MatchResult, related_name="goal_moments", on_delete=models.CASCADE)

    class Meta:
        ordering = ["minute"]
