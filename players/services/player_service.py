import random
from dataclasses import dataclass
from typing import Any
import names
from players import models
from players.models import PlayerPosition


@dataclass
class PlayerGenerator:
    team: Any  # Have to declare type. In reality has to be an instance of Team obv
    lower_end: int
    upper_end: int

    def generate_players(self, amount: int) -> list:
        players = []
        for _ in range(amount):
            player = self.generate_player()
            players.append(player)
        return players

    def generate_player(self):
        player_name = names.get_full_name(gender="male")
        player_position = self._generate_random_pos()
        player_ovr = self._generate_random_overall()
        player = models.Player(
            name=player_name, preferred_position=player_position, team=self.team, overall=player_ovr
        )
        player.save()

        return player

    def _generate_random_overall(self) -> int:
        return random.randint(self.lower_end, self.upper_end)

    @staticmethod
    def _generate_random_pos() -> str:
        positions = [pos for pos in PlayerPosition]
        index = random.randint(0, 2)
        return positions[index]


def get_player_sell_price(player_avg: int, team_avg: int) -> int:
    return 20 - 2 * (team_avg - player_avg)
