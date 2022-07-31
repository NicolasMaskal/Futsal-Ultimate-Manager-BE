from .match_service import TeamSheetPosition
import players.services.match_service as match_service
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


def get_team_average_overall(team) -> int:
    player_amount = 0
    ovr_total = 0
    players = models.Player.objects.filter(current_team=team.id).all()
    for player in players:
        player_amount += 1
        ovr_total += player.overall

    return round(ovr_total / player_amount) if player_amount != 0 else 0


def generate_cpu_overall(team, difficulty_rating: int) -> int:
    team_average = get_team_average_overall(team)
    cpu_average = team_average - 10 + (difficulty_rating * 2)
    return cpu_average


def play_match_against_cpu(player_team_sheet, difficulty_rating: int) -> dict:
    if type(difficulty_rating) != int or difficulty_rating not in range(0, 11):
        raise ValueError("difficulty_rating has to be a number between 0 and 10!")
    player_average = get_teamsheet_average_overall(player_team_sheet, stamina_effect=True)
    cpu_average_overall = generate_cpu_overall(player_team_sheet.team, difficulty_rating)
    match_res = match_service.play_match(player_team_sheet, player_average, cpu_average_overall)
    return dataclasses.asdict(match_res)
