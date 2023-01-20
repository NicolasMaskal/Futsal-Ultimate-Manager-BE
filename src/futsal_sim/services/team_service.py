from django.core.exceptions import ValidationError
from django.db.models import Avg, QuerySet
from rest_framework.generics import get_object_or_404

from src.common.services import model_update
from src.futsal_sim.constants import (
    BASE_COIN_AMOUNT,
    PLAYER_AMOUNT_CREATED_TEAM,
    PLAYER_AMOUNT_TEAM_SHEET,
    SKILL_LOWER_BOUND_CREATED_TEAM,
    SKILL_UPPER_BOUND_CREATED_TEAM,
    TEAM_SKILL_CALC_PLAYER_AMOUNT,
)
from src.futsal_sim.filters import TeamFilter
from src.futsal_sim.models import Player, Team, TeamSheet
from src.futsal_sim.services.factories import PlayerFactory
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
        return get_object_or_404(self.query_set(), id=team_id)  # TODO implement own get_object_or_404 with message

    def team_create(self, *, name: str) -> Team:
        team = Team(name=name, owner=self.user, coins=BASE_COIN_AMOUNT)
        team.full_clean()
        team.save()

        generator = PlayerFactory(
            team=team, lower_b=SKILL_LOWER_BOUND_CREATED_TEAM, upper_b=SKILL_UPPER_BOUND_CREATED_TEAM
        )

        generator.create_players(PLAYER_AMOUNT_CREATED_TEAM)

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


def calc_team_skill(team: Team) -> int:
    # Take x most skillful players and calculate their skill average
    team_skill = (
        Player.objects.filter(team=team.id)
        .order_by("-skill")[:TEAM_SKILL_CALC_PLAYER_AMOUNT]
        .aggregate(Avg("skill"))["skill__avg"]
    )
    return round(team_skill) if team_skill else 0


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


def validate_squad_size(team: Team):
    if not team.has_valid_squad_size:
        raise ValidationError("Invalid squad size. More than 12 players present!")


def team_sell_players(*, team: Team, player_ids: list[int]) -> Team:
    new_squad_size = team.players.count() - len(player_ids)
    if new_squad_size < PLAYER_AMOUNT_TEAM_SHEET:
        raise ValidationError(f"You can't have less than {PLAYER_AMOUNT_TEAM_SHEET} players left!")

    player_qs: QuerySet[Player] = Player.objects.filter(pk__in=player_ids)

    players: list[Player] = list(player_qs.all())
    team_avg = calc_team_skill(team)
    total_sell_price = sum([player.calc_sell_price(team_avg) for player in players])

    player_qs.update(owner=None)

    new_coin_amount = team.coins + total_sell_price
    team, _ = model_update(instance=team, fields=["coins"], data={"coins": new_coin_amount})

    return team
