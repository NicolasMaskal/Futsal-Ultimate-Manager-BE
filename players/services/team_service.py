from match_service import TeamSheetPosition
import match_service
import players.models as models
import dataclasses


def get_teamsheet_average_overall(team_sheet, stamina_effect: bool = False) -> int:
    player_amount = 0
    ovr_total = 0

    for position in TeamSheetPosition:
        player = getattr(team_sheet, position.value)
        if player:
            player_amount += 1
            ovr_total += get_player_ovr_in_position(player, position, stamina_effect)

    return round(ovr_total / player_amount) if player_amount != 0 else 0


def get_player_ovr_in_position(
    player, position: TeamSheetPosition, stamina_effect: bool = False
) -> int:
    stamina_multiplier = player.stamina_left / 100 if stamina_effect else 1
    player_overall = round(stamina_multiplier * player.overall)
    if position == TeamSheetPosition.GOALKEEPER:
        return (
            player_overall if player.preferred_position == TeamSheetPosition.GOALKEEPER.value else 1
        )
    if player.preferred_position == models.PlayerPosition.GOALKEEPER.value:
        return round(0.5 * player_overall)

    multiplier = 1 if player.preferred_position in position.value else 0.75
    return round(multiplier * player_overall)


def play_match_against_cpu(player_team_sheet, cpu_average_overall) -> dict:
    if type(cpu_average_overall) != int or cpu_average_overall not in range(1, 100):
        raise ValueError("Average overall has to be a number between 1 and 100!")
    player_average = get_teamsheet_average_overall(player_team_sheet, stamina_effect=True)
    match_res = match_service.play_match(player_team_sheet, player_average, cpu_average_overall)
    return dataclasses.asdict(match_res)
