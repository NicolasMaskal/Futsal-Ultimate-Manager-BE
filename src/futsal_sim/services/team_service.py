from django.core.exceptions import ValidationError
from django.db.models import Avg, QuerySet
from rest_framework.generics import get_object_or_404

from src.common.services import model_update
from src.futsal_sim.constants import (
    BASE_COIN_AMOUNT,
    PLAYER_AMOUNT_CREATED_TEAM,
    SKILL_LOWER_BOUND_CREATED_TEAM,
    SKILL_UPPER_BOUND_CREATED_TEAM,
)
from src.futsal_sim.filters import TeamFilter
from src.futsal_sim.models import Player, Team, TeamSheet
from src.futsal_sim.services.generators import PlayerGenerator
from src.users.models import User


class TeamCRUDService:
    def __init__(self, *, user: User):
        self.user = user

    def query_set(self) -> QuerySet[Team]:
        if self.user.is_admin:
            return Team.objects.all()
        else:
            return Team.objects.filter(owner=self.user)

    def team_list(self, *, filters=None) -> QuerySet[Team]:
        filters = filters or {}
        qs = self.query_set()
        return TeamFilter(filters, qs).qs

    def team_retrieve(self, *, team_id: int) -> Team:
        return get_object_or_404(self.query_set(), id=team_id)

    def team_create(self, *, name: str) -> Team:
        team = Team(name=name, owner=self.user, coins=BASE_COIN_AMOUNT)
        team.full_clean()
        team.save()

        generator = PlayerGenerator(
            team=team, lower_end=SKILL_LOWER_BOUND_CREATED_TEAM, upper_end=SKILL_UPPER_BOUND_CREATED_TEAM
        )

        generator.generate_players(PLAYER_AMOUNT_CREATED_TEAM)

        if not self.user.active_team:
            self.user.active_team = team
            model_update(instance=self.user, fields=["active_team"], data={"active_team": team})

        return team

    def team_update(self, *, team_id: int, name: str) -> Team:
        team = self.team_retrieve(team_id=team_id)
        team, _ = model_update(instance=team, fields=["name"], data={"name": name})
        return team

    def team_delete(
        self,
        *,
        team_id: int,
    ):
        team = self.team_retrieve(team_id=team_id)
        team.delete()


def calc_team_average_skill(team: Team) -> float:
    average_skill = Player.objects.filter(team=team.id).aggregate(Avg("skill"))["skill__avg"]
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
    new_squad_size = team.players.count() - len(players_to_sell)
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
