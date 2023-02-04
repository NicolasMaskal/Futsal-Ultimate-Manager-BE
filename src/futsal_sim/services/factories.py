import random
from typing import List, Optional, Tuple

import faker
import names

from src.common.utils import get_object
from src.futsal_sim.constants import (
    ASSIST_PERC,
    ATT_GENERATION_PERC_CHANCE,
    ATTACKER_ASSIST_PERC,
    ATTACKER_GOAL_PERC,
    CPU_ATTACKER_LOWER_CONTRIBUTION_MULTIPLIER,
    CPU_ATTACKER_UPPER_CONTRIBUTION_MULTIPLIER,
    CPU_DEFENDER_LOWER_CONTRIBUTION_MULTIPLIER,
    CPU_DEFENDER_UPPER_CONTRIBUTION_MULTIPLIER,
    CPU_GK_LOWER_CONTRIBUTION_MULTIPLIER,
    CPU_GK_UPPER_CONTRIBUTION_MULTIPLIER,
    CPU_MATCHES_PLAYED_LOWER_BOUND,
    CPU_MATCHES_PLAYED_UPPER_BOUND,
    CPU_PLAYER_SKILL_VARIANCE_MULTIPLIER,
    DEF_GENERATION_PERC_CHANCE,
    DEFENDER_ASSIST_PERC,
    DEFENDER_GOAL_PERC,
    GK_ASSIST_PERC,
    GK_GENERATION_PERC_CHANCE,
    GK_GOAL_PERC,
    MAX_CPU_DIFFICULTY_RATING,
    MIN_PLAYER_SKILL,
)
from src.futsal_sim.models import CPUTeam, Player, PlayerPosition, Team, TeamLineup
from src.futsal_sim.services.business_models import TeamSheetPosition


class PositionFactory:
    positions: List[TeamSheetPosition] = [position for position in TeamSheetPosition]

    @staticmethod
    def generate_goal_scorer_position() -> TeamSheetPosition:
        return PositionFactory._generate_position(
            attacker_perc=ATTACKER_GOAL_PERC, defender_perc=DEFENDER_GOAL_PERC, goalkeeper_perc=GK_GOAL_PERC
        )

    @staticmethod
    def generate_assist_maker_position(scorer_pos: TeamSheetPosition) -> Optional[TeamSheetPosition]:
        seed = random.randint(1, 100)
        if seed > ASSIST_PERC:
            return None

        new_pos = scorer_pos
        while new_pos == scorer_pos:
            new_pos = PositionFactory._generate_position(
                attacker_perc=ATTACKER_ASSIST_PERC, defender_perc=DEFENDER_ASSIST_PERC, goalkeeper_perc=GK_ASSIST_PERC
            )

        return new_pos

    @staticmethod
    def _generate_position(*, attacker_perc: int, defender_perc: int, goalkeeper_perc: int) -> TeamSheetPosition:
        if attacker_perc + defender_perc + goalkeeper_perc != 100:
            raise ValueError("Percentages don't add up to 100!")

        seed = random.randint(1, 100)
        side_seed = random.randint(0, 1)
        if seed < attacker_perc:
            return PositionFactory.positions[side_seed]
        elif seed < defender_perc + attacker_perc:
            # First two positions are attackers
            return PositionFactory.positions[2 + side_seed]
        else:
            return TeamSheetPosition.GOALKEEPER


class TeamOpponentFactory:
    def __init__(self, *, player_skill: int, difficulty_rating: int):
        self.player_team_skill = player_skill
        self.difficulty_rating = difficulty_rating
        self.cpu_team_skill = self._calc_cpu_skill()

    def _calc_cpu_skill(self) -> int:
        cpu_average = round(self.player_team_skill - 10 + (self.difficulty_rating * 2))
        return cpu_average

    @staticmethod
    def _generate_random_team_name() -> str:
        abbr = random.choice(["SC", "FC", "FK", "SK"])
        seed = random.randint(0, 1)
        if seed == 0:
            return abbr + " " + faker.Faker().city()
        return faker.Faker().city() + " " + abbr

    def _generate_match_stats_for_team(self, team: Team):
        matches_played = random.randint(CPU_MATCHES_PLAYED_LOWER_BOUND, CPU_MATCHES_PLAYED_UPPER_BOUND)
        difficulty_diff = self.difficulty_rating - MAX_CPU_DIFFICULTY_RATING / 2
        team.wins = round(matches_played * (0.33 + 0.06 * difficulty_diff))
        team.draws = round(matches_played * 0.33)
        team.loses = max(0, round(matches_played * (0.33 - 0.06 * difficulty_diff)))

    def create_cpu_team(self) -> Tuple[Team, TeamLineup]:
        team, lineup = self._find_existing_cpu_by_skill()
        if team and lineup:
            return team, lineup
        return self._generate_cpu_team()

    def _generate_cpu_team(self) -> Tuple[Team, TeamLineup]:
        name = self._generate_random_team_name()
        team = CPUTeam(name=name, skill=self.cpu_team_skill)
        self._generate_match_stats_for_team(team)
        team.save()
        lineup = self._generate_lineup(team)
        return team, lineup

    def _find_existing_cpu_by_skill(self) -> Tuple[Optional[Team], Optional[TeamLineup]]:
        cpu_team = get_object(CPUTeam, skill=self.cpu_team_skill)
        if cpu_team:
            return cpu_team, cpu_team.teamlineup_set.all()[0]

        return None, None

    def _generate_lineup(self, team: Team) -> TeamLineup:
        lower_b = round(self.cpu_team_skill - CPU_PLAYER_SKILL_VARIANCE_MULTIPLIER * self.cpu_team_skill)
        upper_b = round(self.cpu_team_skill + CPU_PLAYER_SKILL_VARIANCE_MULTIPLIER * self.cpu_team_skill)
        player_generator = PlayerFactory(
            team=team,
            lower_b=lower_b,
            upper_b=upper_b,
        )
        right_attacker = player_generator.create_player(
            player_position=PlayerPosition.ATTACKER, generate_with_history=True
        )
        left_attacker = player_generator.create_player(
            player_position=PlayerPosition.ATTACKER, generate_with_history=True
        )
        right_defender = player_generator.create_player(
            player_position=PlayerPosition.DEFENDER, generate_with_history=True
        )
        left_defender = player_generator.create_player(
            player_position=PlayerPosition.DEFENDER, generate_with_history=True
        )
        goalkeeper = player_generator.create_player(
            player_position=PlayerPosition.GOALKEEPER, generate_with_history=True
        )

        lineup = TeamLineup(
            team=team,
            right_attacker=right_attacker,
            left_attacker=left_attacker,
            right_defender=right_defender,
            left_defender=left_defender,
            goalkeeper=goalkeeper,
        )
        lineup.save()
        return lineup


class PlayerFactory:
    def __init__(self, *, team: Team, lower_b: int, upper_b: int):
        self.team = team
        self.skill_lower_b = lower_b
        self.skill_upper_b = upper_b

    def create_players(self, amount: int) -> list[Player]:
        players = []
        for _ in range(amount):
            player = self.create_player()
            players.append(player)
        return players

    def create_player(self, *, generate_with_history: bool = False, player_position: Optional[PlayerPosition] = None):
        player_name = self.generate_random_name()
        player_position = player_position if player_position else self._generate_random_pos()
        player_skill = self._generate_random_skill()
        player = Player(
            name=player_name,
            preferred_position=player_position,
            team=self.team,
            skill=player_skill,
        )
        if generate_with_history:
            self._generate_history_for_player(player)

        player.save()

        return player

    @staticmethod
    def _generate_bounds_for_contributions_multiplier(position: str) -> Tuple[float, float]:
        """
        :param position:
        :return: lower and upper bound for multiplier generation for player contribution (goals scored, assists made)
        """
        match position:
            case PlayerPosition.ATTACKER.value:
                lower_b = CPU_ATTACKER_LOWER_CONTRIBUTION_MULTIPLIER
                upper_b = CPU_ATTACKER_UPPER_CONTRIBUTION_MULTIPLIER
            case PlayerPosition.DEFENDER.value:
                lower_b = CPU_DEFENDER_LOWER_CONTRIBUTION_MULTIPLIER
                upper_b = CPU_DEFENDER_UPPER_CONTRIBUTION_MULTIPLIER
            case PlayerPosition.GOALKEEPER.value:
                lower_b = CPU_GK_LOWER_CONTRIBUTION_MULTIPLIER
                upper_b = CPU_GK_UPPER_CONTRIBUTION_MULTIPLIER
            case _:
                raise ValueError("Invalid player position!")
        return lower_b, upper_b

    def _generate_history_for_player(self, player: Player):
        player.matches_played = random.randint(CPU_MATCHES_PLAYED_LOWER_BOUND, self.team.matches_played)
        lower_b, upper_b = self._generate_bounds_for_contributions_multiplier(player.preferred_position)
        goal_multiplier = random.uniform(lower_b, upper_b)
        assist_multiplier = random.uniform(lower_b, upper_b)
        player.goals_scored = round(goal_multiplier * player.matches_played)
        player.assists_made = round(assist_multiplier * player.matches_played)

    def _generate_random_skill(self) -> int:
        res = random.randint(self.skill_lower_b, self.skill_upper_b)
        return max(res, MIN_PLAYER_SKILL)

    @staticmethod
    def _generate_random_pos() -> PlayerPosition:
        assert GK_GENERATION_PERC_CHANCE + DEF_GENERATION_PERC_CHANCE + ATT_GENERATION_PERC_CHANCE == 100
        seed = random.randint(1, 100)
        if seed <= GK_GENERATION_PERC_CHANCE:
            return PlayerPosition.GOALKEEPER
        if seed <= DEF_GENERATION_PERC_CHANCE + GK_GENERATION_PERC_CHANCE:
            return PlayerPosition.DEFENDER
        return PlayerPosition.ATTACKER

    @staticmethod
    def generate_random_name() -> str:
        return names.get_full_name(gender="male")
