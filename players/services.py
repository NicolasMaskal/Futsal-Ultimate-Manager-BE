import operator
from dataclasses import dataclass
import random
from .models import PlayerTeamSheetLocation, PlayerPosition


@dataclass
class MatchResult:
    home_score: int
    away_score: int


def play_match_against_ai(player_team_sheet, ai_average_overall: int) -> MatchResult:
    player_average = get_average_overall(player_team_sheet)
    return play_match(player_average, ai_average_overall)


def get_average_overall(team_sheet) -> int:
    player_locations = PlayerTeamSheetLocation.objects.filter(team_sheet=team_sheet.id)

    req_positions = [
        PlayerPosition.GOALKEEPER,
        PlayerPosition.DEFENDER * 2,
        PlayerPosition.ATTACKER * 2,
    ]
    if len(req_positions) != len(player_locations):
        raise ValueError("Team sheet doesn't have enough players!")

    total = 0
    player_locations.sort(key=operator.itemgetter(0))  # Sort by pos
    for player_location, req_pos in zip(player_locations, req_positions):
        total += get_player_overall_in_loc(player_location, req_pos)

    return round(total / len(req_positions))


def get_player_overall_in_loc(player_location, req_pos: PlayerPosition) -> int:
    player = player_location.player
    if req_pos == PlayerPosition.GOALKEEPER:
        return player.overall if player.position == PlayerPosition.GOALKEEPER else 1
    else:
        player = player_location.player
        multiplier = 1 if player.position == req_pos else 0.75
        return round(player.overall * multiplier)


def play_match(home_average: int, away_average: int) -> MatchResult:
    total = home_average + away_average
    rand_num = random.randint(1, total)
    if rand_num < home_average:
        return MatchResult(1, 0)
    else:
        return MatchResult(0, 1)
