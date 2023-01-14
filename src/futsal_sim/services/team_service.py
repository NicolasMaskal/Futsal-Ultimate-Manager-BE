import faker
from django.core.exceptions import ValidationError
from django.db.models import Avg

from ...users.models import User
from ..models import Player, Team, TeamSheet


def team_create(*, user: User, name: str) -> Team:
    team = Team(name=name, owner=user)
    team.full_clean()
    team.save()

    if not user.active_team:
        user.active_team = team

    user.save()

    return team


def calc_team_average_skill(team) -> int:
    average_skill = Player.objects.filter(team=team.id).aggregate(Avg("skill"))
    return average_skill if average_skill else 0


def validate_teamsheet_team(*, team: Team, team_sheet: TeamSheet):
    # TODO Replicate logic in input serializer
    if team != team_sheet.team:
        raise ValidationError(f"Team sheet({team_sheet.id}) doesn't belong to team({team_sheet.team.id})!")
    team_sheet_positions = [
        team_sheet.right_attacker,
        team_sheet.left_attacker,
        team_sheet.right_defender,
        team_sheet.left_defender,
        team_sheet.goalkeeper,
    ]
    if None in team_sheet_positions:
        raise ValidationError("Can't play a match with less than 5 players in team sheet!")


def sell_players(*, team: Team, players_to_sell: list[int]):
    new_squad_size = len(team.players) - len(players_to_sell)
    if new_squad_size < 5:
        raise ValidationError("You can't have less than 5 players left!")
    team_avg = calc_team_average_skill(team)
    for player_id in players_to_sell:
        player = Player.objects.get(player_id)
        sell_price = player.calc_sell_price(team_avg)
        team.coins += sell_price
        player.delete()
    team.save()


def validate_squad_size(team: Team):
    if not team.has_valid_squad_size:
        raise ValidationError("Invalid squad size. More than 12 players present!")


def generate_random_cpu_team_name() -> str:
    return "FC " + faker.Faker().city()
