from .match_service import TeamSheetPosition
import players.services.match_service as match_service
import players.services.player_service as player_service
import players.models as models
import dataclasses


def get_teamsheet_average_skill(team_sheet, stamina_effect: bool = False) -> int:
    player_amount = 0
    skill_total = 0

    for position in TeamSheetPosition:
        player = getattr(team_sheet, position.value)
        if player:
            player_amount += 1
            skill_total += player_service.get_player_skill_in_position(
                player, position, stamina_effect
            )

    return round(skill_total / player_amount) if player_amount != 0 else 0


def get_team_average_skill(team) -> int:
    player_amount = 0
    skill_total = 0
    players = models.Player.objects.filter(team=team.id).all()
    for player in players:
        player_amount += 1
        skill_total += player.skill

    return round(skill_total / player_amount) if player_amount != 0 else 0


def generate_cpu_skill(team, difficulty_rating: int) -> int:
    team_average = get_team_average_skill(team)
    cpu_average = team_average - 10 + (difficulty_rating * 2)
    return cpu_average


def play_match_against_cpu(player_team_sheet, difficulty_rating: int) -> dict:
    if type(difficulty_rating) != int or difficulty_rating not in range(0, 11):
        raise ValueError("difficulty_rating has to be a number between 0 and 10!")
    player_average = get_teamsheet_average_skill(player_team_sheet, stamina_effect=True)
    cpu_average_skill = generate_cpu_skill(player_team_sheet.team, difficulty_rating)
    match_res = match_service.play_match(player_team_sheet, player_average, cpu_average_skill)
    return dataclasses.asdict(match_res)


def get_match_results(team) -> list:
    match_results = models.MatchResult.objects.filter(player_team=team)
    return match_results


def validate_teamsheet_team(team, team_sheet):
    if team != team_sheet.team:
        raise ValueError(
            f"Team_sheet({team_sheet.id}) doesn't belong to team({team_sheet.team.id})!"
        )


def sell_players(team, players: list):
    team_players = player_service.get_players_of_team(team)
    new_squad_size = len(team_players) - len(players)
    if new_squad_size < 5:
        raise ValueError("You can't have less than 5 players left!")
    team_avg = get_team_average_skill(team)
    for player_id in players:
        player = player_service.get_player(player_id)
        sell_price = player_service.get_player_sell_price(player, team_avg)
        team.coins += sell_price
        player.delete()
    team.save()
