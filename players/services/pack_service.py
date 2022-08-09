from enum import Enum
from typing import Tuple

from players.services import team_service, player_service


class PackType(Enum):
    BRONZE = 100
    SILVER = 200
    GOLD = 400


def _get_lower_upper_bounds(team, pack_type: PackType) -> Tuple[int, int]:
    avg_skill = team_service.get_team_average_skill(team)
    if pack_type == PackType.GOLD:
        lower_end = avg_skill
        upper_end = avg_skill + 8
    elif pack_type == PackType.SILVER:
        lower_end = avg_skill - 3
        upper_end = avg_skill + 3
    else:  # Bronze
        lower_end = avg_skill - 10
        upper_end = avg_skill
    return lower_end, upper_end


def _validate_pack_type(pack_type: str) -> PackType:
    pack_type = pack_type.lower()
    pack_types = dict(gold=PackType.GOLD, silver=PackType.SILVER, bronze=PackType.BRONZE)
    if pack_type not in pack_types:
        raise ValueError(f"{pack_type} is not a valid pack type!")
    return pack_types[pack_type]


def _validate_team_coins(team, pack_type: PackType):
    if team.coins < pack_type.value:
        raise ValueError(f"Not enough coins to buy this pack!")
    team.coins -= pack_type.value


def buy_pack(team, pack_type_str: str) -> list:
    pack_type = _validate_pack_type(pack_type_str)
    print(pack_type)
    _validate_team_coins(team, pack_type)

    lower_b, upper_b = _get_lower_upper_bounds(team, pack_type)
    generator = player_service.PlayerGenerator(team, lower_b, upper_b)
    players = generator.generate_players(3)

    team.save()  # Save spent coins
    return players
