from dataclasses import dataclass
import random
from .models import PlayerPosition


@dataclass
class MatchResult:
    home_score: int
    away_score: int


def play_match_against_ai(player_team_sheet, ai_average_overall: int) -> MatchResult:
    player_average = get_team_average_overall(player_team_sheet)
    return play_match(player_average, ai_average_overall)


def get_team_average_overall(team_sheet) -> int:
    positions = ["right_attacker", "left_attacker", "right_defender", "left_defender", "goalkeeper"]
    player_amount = 0
    ovr_total = 0

    for position in positions:
        player = getattr(team_sheet, position)
        if player:
            player_amount += 1
            ovr_total += get_player_ovr_in_position(player, position)

    return round(ovr_total/player_amount) if player_amount != 0 else 0


def get_player_ovr_in_position(player, position) -> int:
    if position == PlayerPosition.GOALKEEPER:
        return player.overall if player.preferred_position == position else 1
    if player.preferred_position == PlayerPosition.GOALKEEPER:
        return round(0.5 * player.overall)

    multiplier = 1 if player.preferred_position in position else 0.75
    return round(multiplier * player.overall)


def play_match(home_average: int, away_average: int) -> MatchResult:
    total = home_average + away_average
    rand_num = random.randint(1, total)
    if rand_num < home_average:
        return MatchResult(1, 0)
    else:
        return MatchResult(0, 1)