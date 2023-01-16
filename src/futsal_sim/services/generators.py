import random

import faker
import names

from src.futsal_sim.constants import (
    ATT_GENERATION_PERC_CHANCE,
    DEF_GENERATION_PERC_CHANCE,
    GK_GENERATION_PERC_CHANCE,
)
from src.futsal_sim.models import Player, PlayerPosition, Team
from src.futsal_sim.services.business_models import CpuTeamSheetNames


def generate_random_cpu_team_name() -> str:
    return "FC " + faker.Faker().city()


def generate_random_cpu_teamsheet() -> CpuTeamSheetNames:
    return CpuTeamSheetNames(
        right_attacker=PlayerGenerator.generate_random_name(),
        left_attacker=PlayerGenerator.generate_random_name(),
        right_defender=PlayerGenerator.generate_random_name(),
        left_defender=PlayerGenerator.generate_random_name(),
        goalkeeper=PlayerGenerator.generate_random_name(),
    )


class PlayerGenerator:
    def __init__(self, *, team: Team, lower_end: int, upper_end: int):
        self.team = team
        self.lower_end = lower_end
        self.upper_end = upper_end

    def generate_players(self, amount: int) -> list[Player]:
        players = []
        for _ in range(amount):
            player = self.generate_player()
            players.append(player)
        return players

    def generate_player(self):
        player_name = self.generate_random_name()
        player_position = self._generate_random_pos()
        player_skill = self._generate_random_skill()
        player = Player(
            name=player_name,
            preferred_position=player_position,
            team=self.team,
            skill=player_skill,
        )
        player.save()

        return player

    def _generate_random_skill(self) -> int:
        return random.randint(self.lower_end, self.upper_end)

    @staticmethod
    def _generate_random_pos() -> str:
        assert GK_GENERATION_PERC_CHANCE + DEF_GENERATION_PERC_CHANCE + ATT_GENERATION_PERC_CHANCE == 100
        seed = random.randint(1, 100)
        if seed <= GK_GENERATION_PERC_CHANCE:
            return PlayerPosition.GOALKEEPER
        if seed <= DEF_GENERATION_PERC_CHANCE + GK_GENERATION_PERC_CHANCE:
            return PlayerPosition.DEFENDER
        return PlayerPosition.ATTACKER

    @staticmethod
    def generate_random_name() -> str:
        return names.get_full_name(gender="male")
