from enum import Enum
from typing import Tuple

from django.core.exceptions import ValidationError

from src.futsal_sim.constants import (
    BRONZE_LOWER_BOUND,
    BRONZE_PRICE,
    BRONZE_UPPER_BOUND,
    GOLD_LOWER_BOUND,
    GOLD_PRICE,
    GOLD_UPPER_BOUND,
    PLAYER_AMOUNT_IN_PACK,
    SILVER_LOWER_BOUND,
    SILVER_PRICE,
    SILVER_UPPER_BOUND,
)
from src.futsal_sim.models import Team
from src.futsal_sim.services.factories import PlayerFactory
from src.futsal_sim.services.team_service import calc_team_skill


class PackType(Enum):
    BRONZE = BRONZE_PRICE
    SILVER = SILVER_PRICE
    GOLD = GOLD_PRICE


def _get_lower_upper_bounds(team: Team, pack_type: PackType) -> Tuple[int, int]:
    team_skill = calc_team_skill(team)
    match pack_type:
        case PackType.GOLD:
            lower_end = team_skill + GOLD_LOWER_BOUND
            upper_end = team_skill + GOLD_UPPER_BOUND
        case PackType.SILVER:
            lower_end = team_skill + SILVER_LOWER_BOUND
            upper_end = team_skill + SILVER_UPPER_BOUND
        case PackType.BRONZE:
            lower_end = team_skill + BRONZE_LOWER_BOUND
            upper_end = team_skill + BRONZE_UPPER_BOUND
        case _:
            raise ValueError("Invalid pack type detected!")

    return round(lower_end), round(upper_end)


def get_pack_by_pack_type(pack_type: str) -> PackType:
    pack_type = pack_type.lower()
    pack_types = dict(gold=PackType.GOLD, silver=PackType.SILVER, bronze=PackType.BRONZE)
    if pack_type not in pack_types:
        raise ValueError(f"{pack_type} is not a valid pack type!")
    return pack_types[pack_type]


def _validate_team_coins(*, team: Team, pack_type: PackType):
    if team.coins < pack_type.value:
        raise ValidationError("Not enough coins to buy this pack!")


def buy_pack(*, team: Team, pack_type: str) -> list:
    pack_type_obj = get_pack_by_pack_type(pack_type)
    _validate_team_coins(team=team, pack_type=pack_type_obj)
    team.coins -= pack_type_obj.value

    lower_b, upper_b = _get_lower_upper_bounds(team, pack_type_obj)
    generator = PlayerFactory(team=team, lower_b=lower_b, upper_b=upper_b)
    players = generator.create_players(PLAYER_AMOUNT_IN_PACK)

    team.save()  # Save spent coins
    return players
