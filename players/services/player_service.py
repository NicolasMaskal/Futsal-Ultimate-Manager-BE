import random
from dataclasses import dataclass
from typing import Any
import names
from players import models
from players.models import PlayerPosition, Player
from players.services.match_service import TeamSheetPosition


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
        player_skill = self._generate_random_skill()
        player = models.Player(
            name=player_name, preferred_position=player_position, team=self.team, skill=player_skill
        )
        player.save()

        return player

    def _generate_random_skill(self) -> int:
        return random.randint(self.lower_end, self.upper_end)

    @staticmethod
    def _generate_random_pos() -> str:
        positions = [pos for pos in PlayerPosition]
        index = random.randint(0, 2)
        return positions[index]


def get_player_sell_price(player, team_avg: int) -> int:
    sell_price = 20 - team_avg + player.skill
    return max(sell_price, 5)


def get_players_of_team(team) -> list:
    return Player.objects.filter(team=team)


def get_player(player_id):
    return Player.objects.get(id=player_id)


def get_player_skill_in_position(
    player, position: TeamSheetPosition, stamina_effect: bool = False
) -> int:
    stamina_multiplier = player.stamina_left / 100 if stamina_effect else 1
    player_skill = round(stamina_multiplier * player.skill)
    if position == TeamSheetPosition.GOALKEEPER:
        multiplier = 1 if player.preferred_position == TeamSheetPosition.GOALKEEPER.value else 0.25
    elif player.preferred_position == models.PlayerPosition.GOALKEEPER.value:
        multiplier = 0.5  # deffo is a Gk playing in an infield position
    else:
        multiplier = 1 if player.preferred_position in position.value else 0.75

    player_skill_pos = round(multiplier * player_skill)
    return max(1, player_skill_pos)
