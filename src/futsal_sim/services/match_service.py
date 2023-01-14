import dataclasses
import random
from dataclasses import dataclass
from typing import List, Optional

from src.futsal_sim.constants import (
    ATTACKER_ASSIST_PERC,
    ATTACKER_GOAL_PERC,
    DEFENDER_ASSIST_PERC,
    DEFENDER_GOAL_PERC,
    GK_ASSIST_PERC,
    GK_GOAL_PERC,
    GOAL_AMOUNT_GENERATION_ITERATIONS,
    MAX_GOAL_AMOUNT,
    MIN_GOAL_AMOUNT,
    MULTIPLIER_COIN_DRAW,
    MULTIPLIER_COIN_LOSS,
)
from src.futsal_sim.models import MatchResult, Team, TeamSheet

from .business_models import MatchResultOutput, TeamSheetPosition
from .generators import generate_random_cpu_team_name
from .team_service import calc_team_average_skill
from .teamsheet_service import (
    calc_teamsheet_average_skill,
    generate_random_cpu_teamsheet,
)


class PositionGenerator:
    positions: List[TeamSheetPosition] = [position for position in TeamSheetPosition]

    @staticmethod
    def generate_goal_scorer_position() -> TeamSheetPosition:
        return PositionGenerator._generate_position(
            attacker_perc=ATTACKER_GOAL_PERC, defender_perc=DEFENDER_GOAL_PERC, goalkeeper_perc=GK_GOAL_PERC
        )

    @staticmethod
    def generate_assist_maker_position() -> Optional[TeamSheetPosition]:
        seed = random.randint(1, 100)
        if seed <= 60:
            return PositionGenerator._generate_position(
                attacker_perc=ATTACKER_ASSIST_PERC, defender_perc=DEFENDER_ASSIST_PERC, goalkeeper_perc=GK_ASSIST_PERC
            )
        return None

    @staticmethod
    def _generate_position(*, attacker_perc: int, defender_perc: int, goalkeeper_perc: int) -> TeamSheetPosition:
        if attacker_perc + defender_perc + goalkeeper_perc != 100:
            raise ValueError("Percentages don't add up to 100!")

        seed = random.randint(1, 100)
        side_seed = random.randint(0, 1)
        if seed < attacker_perc:
            return PositionGenerator.positions[side_seed]
        elif seed < defender_perc + attacker_perc:
            # First two positions are attackers
            return PositionGenerator.positions[2 + side_seed]
        else:
            return TeamSheetPosition.GOALKEEPER


class TeamSheetInMatchManager:
    def __init__(self, team_sheet: TeamSheet):
        self.team_sheet = team_sheet

    def generate_scorer_update(self) -> TeamSheetPosition:
        """
        :return: Position of scorer
        """
        position = PositionGenerator.generate_goal_scorer_position()
        player = getattr(self.team_sheet, position.value)

        player.goals_scored += 1
        return position

    def generate_assister_update(self, scorer_position: TeamSheetPosition) -> Optional[TeamSheetPosition]:
        position = PositionGenerator.generate_assist_maker_position()
        while position == scorer_position:
            position = PositionGenerator.generate_assist_maker_position()

        if position:
            player = getattr(self.team_sheet, position.value)
            player.assists_made += 1
        return position

    def update_stamina(self):
        for position in PositionGenerator.positions:
            player = getattr(self.team_sheet, position.value)
            stamina_drained = random.randint(27, 33)
            if position == TeamSheetPosition.GOALKEEPER:
                # Goalkeepers aren't as tired as other positions
                stamina_drained = round(0.5 * stamina_drained)

            new_stamina = player.stamina_left - stamina_drained
            new_stamina = min(100, new_stamina)
            player.stamina_left = max(1, new_stamina)

    def handle_match_finished(self):
        # self.update_stamina() Not for now TODO
        for position in PositionGenerator.positions:
            player = getattr(self.team_sheet, position.value)
            player.matches_played += 1
            player.save()


@dataclass
class _Match:
    player_average: int
    cpu_average: int
    player_team: Team
    team_sheet_manager: TeamSheetInMatchManager
    player_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    cpu_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    player_goal_scorers: List[TeamSheetPosition] = dataclasses.field(default_factory=lambda: [])
    cpu_goal_scorers: List[TeamSheetPosition] = dataclasses.field(default_factory=lambda: [])
    player_assist_makers: List[Optional[TeamSheetPosition]] = dataclasses.field(default_factory=lambda: [])
    cpu_assist_makers: List[Optional[TeamSheetPosition]] = dataclasses.field(default_factory=lambda: [])

    def play_match(self) -> MatchResultOutput:
        # using min so that lower scores are more common
        goal_amount = min(
            random.randint(MIN_GOAL_AMOUNT, MAX_GOAL_AMOUNT) for _ in range(GOAL_AMOUNT_GENERATION_ITERATIONS)
        )

        for i in range(goal_amount):
            self._add_goal_to_score()

        return self._create_match_result_from_score()

    def _create_match_result_from_score(self) -> MatchResultOutput:
        self.player_goals_minutes.sort()
        self.cpu_goals_minutes.sort()
        cpu_team_name = generate_random_cpu_team_name()
        MatchResult(
            cpu_team_name=cpu_team_name,
            player_score=self.get_player_goal_amount(),
            cpu_score=self.get_cpu_goal_amount(),
            cpu_average_skill=self.cpu_average,
            player_team=self.player_team,
        ).save()

        added_coins = self.update_team_with_result()

        self.team_sheet_manager.handle_match_finished()

        return MatchResultOutput(
            coins_reward=added_coins,
            player_average_skill=self.player_average,
            cpu_average_skill=self.cpu_average,
            cpu_team_name=cpu_team_name,
            player_goals=self.get_player_goal_amount(),
            cpu_goals=self.get_cpu_goal_amount(),
            player_goals_minutes=self.player_goals_minutes,
            cpu_goals_minutes=self.cpu_goals_minutes,
            player_goal_scorers=self.player_goal_scorers,
            cpu_goal_scorers=self.cpu_goal_scorers,
            player_assist_makers=self.player_assist_makers,
            cpu_assist_makers=self.cpu_assist_makers,
            cpu_team_sheet=generate_random_cpu_teamsheet(),
        )

    def _add_goal_to_score(self):
        player_goal_chance = 50 + self.player_average - self.cpu_average

        seed = random.randint(1, 100)
        if seed < player_goal_chance:
            self._add_player_goal()
        else:
            self._add_cpu_goal()

    def _add_player_goal(self):
        scorer_pos = self.team_sheet_manager.generate_scorer_update()
        self.player_goal_scorers.append(scorer_pos)

        assister_pos = self.team_sheet_manager.generate_assister_update(scorer_pos)
        self.player_assist_makers.append(assister_pos)

        time_of_goal = self.generate_random_minute()
        self.player_goals_minutes.append(time_of_goal)

    def _add_cpu_goal(self):
        scorer_pos = PositionGenerator.generate_goal_scorer_position()
        self.cpu_goal_scorers.append(scorer_pos)

        assister_pos = PositionGenerator.generate_assist_maker_position()
        self.cpu_assist_makers.append(assister_pos)

        time_of_goal = self.generate_random_minute()
        self.cpu_goals_minutes.append(time_of_goal)

    def generate_random_minute(self) -> int:
        random_minute = random.randint(1, 90)
        while random_minute in self.player_goals_minutes + self.cpu_goals_minutes:
            random_minute = random.randint(1, 90)
        return random_minute

    def update_team_with_result(self) -> int:
        """
        :return: coins gained
        """
        player_goals = self.get_player_goal_amount()
        cpu_goals = self.get_cpu_goal_amount()

        added_coins_for_win = 50 + 5 * (self.cpu_average - self.player_average)
        if player_goals > cpu_goals:
            self.player_team.wins += 1
            added_coins = added_coins_for_win + player_goals - cpu_goals
        elif player_goals == cpu_goals:
            self.player_team.draws += 1
            added_coins = round(added_coins_for_win * MULTIPLIER_COIN_DRAW)
        else:
            self.player_team.loses += 1
            added_coins = round(added_coins_for_win * MULTIPLIER_COIN_LOSS)
            added_coins += player_goals - cpu_goals

        added_coins = max(added_coins, 0)
        self.player_team.coins += added_coins
        self.player_team.save()
        return added_coins

    def get_player_goal_amount(self) -> int:
        return len(self.player_goals_minutes)

    def get_cpu_goal_amount(self) -> int:
        return len(self.cpu_goals_minutes)


def generate_cpu_skill(*, team: Team, difficulty_rating: int) -> int:
    team_average = calc_team_average_skill(team)
    cpu_average = team_average - 10 + (difficulty_rating * 2)
    return cpu_average


def play_match_against_cpu(*, player_team: Team, player_team_sheet: TeamSheet, difficulty_rating: int) -> dict:
    player_average = calc_teamsheet_average_skill(player_team_sheet)
    cpu_average_skill = generate_cpu_skill(team=player_team, difficulty_rating=difficulty_rating)
    team_sheet_manager = TeamSheetInMatchManager(player_team_sheet)
    match = _Match(player_average, cpu_average_skill, player_team, team_sheet_manager)
    match_res = match.play_match()
    return match_res.__dict__
