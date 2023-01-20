from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from src.common.services import model_update
from src.futsal_sim.filters import TeamSheetFilter
from src.futsal_sim.models import Team, TeamLineup, TeamPlayersInPositions, TeamSheet

from .business_models import TeamSheetPosition
from .player_service import PlayerSkillCalculator


class TeamSheetCRUDService:
    def __init__(self, *, team: Team):
        self.team = team

    def query_set(self) -> QuerySet[TeamSheet]:
        return TeamSheet.objects.filter(team=self.team)

    def teamsheet_list(self, filters=None) -> QuerySet[TeamSheet]:
        filters = filters or {}
        qs = self.query_set()
        return TeamSheetFilter(filters, qs).qs

    def teamsheet_retrieve(self, *, teamsheet_id: int):
        return get_object_or_404(self.query_set(), id=teamsheet_id)

    def teamsheet_create(
        self,
        *,
        name: str,
        right_attacker: int,
        left_attacker: int,
        right_defender: int,
        left_defender: int,
        goalkeeper: int
    ) -> TeamSheet:
        team_sheet = TeamSheet(
            name=name,
            right_attacker_id=right_attacker,
            left_attacker_id=left_attacker,
            right_defender_id=right_defender,
            left_defender_id=left_defender,
            goalkeeper_id=goalkeeper,
            team=self.team,
        )
        team_sheet.full_clean()
        team_sheet.save()

        return team_sheet

    def teamsheet_update(
        self,
        *,
        teamsheet_id: int,
        name: str,
        right_attacker: int,
        left_attacker: int,
        right_defender: int,
        left_defender: int,
        goalkeeper: int
    ) -> TeamSheet:
        teamsheet = self.teamsheet_retrieve(teamsheet_id=teamsheet_id)
        teamsheet, _ = model_update(
            instance=teamsheet,
            fields=[
                "name",
                "right_attacker_id",
                "left_attacker_id",
                "right_defender_id",
                "left_defender_id",
                "goalkeeper_id",
            ],
            data={
                "name": name,
                "right_attacker_id": right_attacker,
                "left_attacker_id": left_attacker,
                "right_defender_id": right_defender,
                "left_defender_id": left_defender,
                "goalkeeper_id": goalkeeper,
            },
        )
        return teamsheet

    def teamsheet_delete(self, teamsheet_id: int):
        teamsheet = self.teamsheet_retrieve(teamsheet_id=teamsheet_id)
        teamsheet.delete()


def calc_sheet_lineup_average_skill(team_sheet_or_lineup: TeamPlayersInPositions) -> int:
    player_amount = 0
    skill_total = 0

    position: TeamSheetPosition
    for position in TeamSheetPosition:
        player = getattr(team_sheet_or_lineup, position.value)
        if player:
            player_amount += 1
            skill_total += PlayerSkillCalculator(player=player, cur_pos=position).calc_skill_in_pos()

    return round(skill_total / player_amount) if player_amount != 0 else 0


def validate_teamsheet_can_play_match(team_sheet: TeamSheet):
    if not team_sheet.is_ready_for_match:
        raise ValidationError("Team sheet isn't ready for match!")


def create_lineup_from_sheet(team_sheet: TeamSheet) -> TeamLineup:
    lineup = TeamLineup(
        team=team_sheet.team,
        right_attacker=team_sheet.right_attacker,
        left_attacker=team_sheet.left_attacker,
        right_defender=team_sheet.right_defender,
        left_defender=team_sheet.left_defender,
        goalkeeper=team_sheet.goalkeeper,
    )
    lineup.save()
    return lineup
