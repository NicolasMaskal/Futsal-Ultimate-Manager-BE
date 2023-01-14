from enum import Enum
from typing import Tuple

from rest_framework.exceptions import ValidationError

from src.futsal_sim.constants import (
    BRONZE_LOWER_BOUND,
    BRONZE_PRICE,
    BRONZE_UPPER_BOUND,
    GOLD_LOWER_BOUND,
    GOLD_PRICE,
    GOLD_UPPER_BOUND,
    SILVER_LOWER_BOUND,
    SILVER_PRICE,
    SILVER_UPPER_BOUND,
)

from ..models import Team
from .player_service import PlayerGenerator
from .team_service import calc_team_average_skill


class PackType(Enum):
    BRONZE = BRONZE_PRICE
    SILVER = SILVER_PRICE
    GOLD = GOLD_PRICE


def _get_lower_upper_bounds(team, pack_type: PackType) -> Tuple[int, int]:
    avg_skill = calc_team_average_skill(team)
    match pack_type:
        case [PackType.GOLD]:
            lower_end = avg_skill + GOLD_LOWER_BOUND
            upper_end = avg_skill + GOLD_UPPER_BOUND
        case [PackType.SILVER]:
            lower_end = avg_skill + SILVER_LOWER_BOUND
            upper_end = avg_skill + SILVER_UPPER_BOUND
        case [PackType.BRONZE]:
            lower_end = avg_skill + BRONZE_LOWER_BOUND
            upper_end = avg_skill + BRONZE_UPPER_BOUND
        case _:
            raise ValueError("Invalid pack type detected!")

    return lower_end, upper_end


def _validate_pack_type(pack_type: str) -> PackType:
    pack_type = pack_type.lower()
    pack_types = dict(gold=PackType.GOLD, silver=PackType.SILVER, bronze=PackType.BRONZE)
    if pack_type not in pack_types:
        raise ValueError(f"{pack_type} is not a valid pack type!")
    return pack_types[pack_type]


def _validate_team_coins(team: Team, pack_type: PackType):
    if team.coins < pack_type.value:
        raise ValidationError("Not enough coins to buy this pack!")


def buy_pack(team: Team, pack_type_str: str) -> list:
    pack_type = _validate_pack_type(pack_type_str)
    print(pack_type)
    _validate_team_coins(team, pack_type)
    team.coins -= pack_type.value

    lower_b, upper_b = _get_lower_upper_bounds(team, pack_type)
    generator = PlayerGenerator(team=team, lower_end=lower_b, upper_end=upper_b)
    players = generator.generate_players(3)

    team.save()  # Save spent coins
    return players
