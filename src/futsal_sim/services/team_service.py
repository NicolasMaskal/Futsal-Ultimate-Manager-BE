from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Avg, Q, QuerySet

from src.common.services import model_update
from src.common.utils import find_or_fail
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
            return Team.objects.filter(Q(owner=self.user) | Q(owner__isnull=True))

    def team_list(self, *, filters=None) -> QuerySet[Team]:
        filters = filters or {}
        qs = self.query_set()
        return TeamFilter(filters, qs).qs

    def team_retrieve(self, *, team_id: int) -> Team:
        return find_or_fail(self.query_set(), error_message=f"Team with id={team_id} not found!", id=team_id)

    def team_create(self, *, name: str) -> Team:
        team = Team(name=name, owner=self.user, coins=BASE_COIN_AMOUNT)
        team.full_clean()
        team.save()

        generator = PlayerFactory(
            team=team, lower_b=SKILL_LOWER_BOUND_CREATED_TEAM, upper_b=SKILL_UPPER_BOUND_CREATED_TEAM
        )

        generator.create_players(PLAYER_AMOUNT_CREATED_TEAM)

        if not self.user.active_team:
            # self.user.active_team = team
            model_update(instance=self.user, fields=["active_team"], data={"active_team": team})

        return team

    def team_update(self, *, team_id: int, name: str) -> Team:
        team = self.team_retrieve(team_id=team_id)
        validate_owner_of_team_perms(team=team, user=self.user)
        team, _ = model_update(instance=team, fields=["name"], data={"name": name})
        return team

    def team_delete(
        self,
        *,
        team_id: int,
    ):
        team = self.team_retrieve(team_id=team_id)
        validate_owner_of_team_perms(team=team, user=self.user)
        team.delete()


def validate_owner_of_team_perms(*, user: User, team: Team):
    """
    Validates that team is user owned, and that team is user-owned by user or is admin.
    If team is
    :param user:
    :param team:
    :return:
    """

    if not team.owner or (not user.is_admin and team.owner != user):
        raise PermissionDenied("Only team owners can perform this action!")


def calc_team_skill(team: Team) -> int:
    # Take x most skillful players and calculate their skill average
    team_skill = (
        Player.objects.filter(team=team.id)
        .order_by("-skill")[:TEAM_SKILL_CALC_PLAYER_AMOUNT]
        .aggregate(Avg("skill"))["skill__avg"]
    )
    return round(team_skill) if team_skill else 0


def calc_average_skill(team: Team) -> int:
    average_player_skill = Player.objects.filter(team=team.id).aggregate(Avg("skill"))["skill__avg"]
    return round(average_player_skill) if average_player_skill else 0


def team_sell_players(*, team: Team, player_ids: list[int], user: User) -> Team:
    validate_owner_of_team_perms(team=team, user=user)
    new_squad_size = team.players.count() - len(player_ids)
    if new_squad_size < PLAYER_AMOUNT_TEAM_SHEET:
        raise ValidationError(
            f"Error selling player(s), you can't have less than {PLAYER_AMOUNT_TEAM_SHEET} players left!"
        )

    player_qs: QuerySet[Player] = Player.objects.filter(pk__in=player_ids)

    players: list[Player] = list(player_qs.all())
    team_avg = calc_team_skill(team)
    total_sell_price = sum([player.calc_sell_price(team_avg) for player in players])

    player_qs.update(team=None)
    update_sheets_after_sell(player_qs)

    new_coin_amount = team.coins + total_sell_price
    team, _ = model_update(instance=team, fields=["coins"], data={"coins": new_coin_amount})

    return team


def update_sheets_after_sell(player_qs: QuerySet[Player]):
    # Get all team sheets related to the sold players
    team_sheets_qs = TeamSheet.objects.filter(
        Q(right_attacker__in=player_qs)
        | Q(left_attacker__in=player_qs)
        | Q(right_defender__in=player_qs)
        | Q(left_defender__in=player_qs)
        | Q(goalkeeper__in=player_qs)
    )

    # Loop through each sheet and set the related position to null
    for team_sheet in team_sheets_qs:
        if team_sheet.right_attacker in player_qs:
            team_sheet.right_attacker = None
        elif team_sheet.left_attacker in player_qs:
            team_sheet.left_attacker = None
        elif team_sheet.right_defender in player_qs:
            team_sheet.right_defender = None
        elif team_sheet.left_defender in player_qs:
            team_sheet.left_defender = None
        elif team_sheet.goalkeeper in player_qs:
            team_sheet.goalkeeper = None
        team_sheet.save()
