from src.futsal_sim.models import TeamSheet

from .business_models import CpuTeamSheetNames, TeamSheetPosition
from .generators import PlayerGenerator
from .player_service import PlayerSkillCalculator


def calc_teamsheet_average_skill(team_sheet: TeamSheet) -> int:
    player_amount = 0
    skill_total = 0

    position: TeamSheetPosition
    for position in TeamSheetPosition:
        player = getattr(team_sheet, position.value)
        if player:
            player_amount += 1
            skill_total = PlayerSkillCalculator(player=player, cur_pos=position).calc_skill_in_pos()

    return round(skill_total / player_amount) if player_amount != 0 else 0


def generate_random_cpu_teamsheet() -> CpuTeamSheetNames:
    return CpuTeamSheetNames(
        right_attacker=PlayerGenerator.generate_random_name(),
        left_attacker=PlayerGenerator.generate_random_name(),
        right_defender=PlayerGenerator.generate_random_name(),
        left_defender=PlayerGenerator.generate_random_name(),
        goalkeeper=PlayerGenerator.generate_random_name(),
    )