import dataclasses
from dataclasses import dataclass
import random
from .models import PlayerPosition
from typing import List, Optional
from enum import Enum


class TeamSheetPosition(Enum):
    RIGHT_ATTACKER = "right_attacker"
    LEFT_ATTACKER = "left_attacker"
    RIGHT_DEFENDER = "right_defender"
    LEFT_DEFENDER = "left_defender"
    GOALKEEPER = "goalkeeper"


@dataclass
class MatchResult:
    home_goals: int
    away_goals: int
    home_goals_minutes: List[int]
    away_goals_minutes: List[int]


@dataclass
class _Match:
    home_average: int
    away_average: int
    home_goals: int = 0
    away_goals: int = 0
    home_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    away_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])

    def play_match(self) -> MatchResult:
        # using min so that lower scores are more common
        goal_amount = min(random.randint(1, 12) for _ in range(3))
        for i in range(goal_amount):
            self._add_goal_to_score()

        return self._create_match_result_from_score()

    def _create_match_result_from_score(self) -> MatchResult:
        self.home_goals_minutes.sort()
        self.away_goals_minutes.sort()
        return MatchResult(
            home_goals=self.home_goals,
            away_goals=self.away_goals,
            home_goals_minutes=self.home_goals_minutes.copy(),
            away_goals_minutes=self.away_goals_minutes.copy(),
        )

    def _add_goal_to_score(self):
        home_goal_chance = 50 + round(self.home_average - self.away_average)

        seed = random.randint(1, 100)
        if seed < home_goal_chance:
            self._add_home_goal()
        else:
            self._add_away_goal()

    def is_draw(self) -> bool:
        return self.home_goals == self.away_goals

    def _add_home_goal(self):
        self.home_goals += 1
        time_of_goal = self.generate_random_minute()
        self.home_goals_minutes.append(time_of_goal)

    def _add_away_goal(self):
        self.away_goals += 1
        time_of_goal = self.generate_random_minute()
        self.away_goals_minutes.append(time_of_goal)

    @staticmethod
    def generate_random_minute() -> int:
        return random.randint(1, 90)


def generate_goal_scorer() -> TeamSheetPosition:
    pass


def generate_assist_maker() -> Optional[TeamSheetPosition]:
    pass


def play_match_against_ai(player_team_sheet, ai_average_overall) -> dict:
    # TODO Create dict team sheet that will be then updated
    if type(ai_average_overall) != int or ai_average_overall not in range(1, 100):
        raise ValueError("Average overall has to be a number between 1 and 100!")
    player_average = get_team_average_overall(player_team_sheet)
    match = _Match(player_average, ai_average_overall)
    match_result = match.play_match()
    return dataclasses.asdict(match_result)


def get_team_average_overall(team_sheet) -> int:
    player_amount = 0
    ovr_total = 0

    for position in TeamSheetPosition:
        player = getattr(team_sheet, position.value)
        if player:
            player_amount += 1
            ovr_total += get_player_ovr_in_position(player, position)

    return round(ovr_total / player_amount) if player_amount != 0 else 0


def get_player_ovr_in_position(player, position: TeamSheetPosition) -> int:
    if position == TeamSheetPosition.GOALKEEPER:
        return player.overall if player.preferred_position == TeamSheetPosition.GOALKEEPER.value else 1
    if player.preferred_position == PlayerPosition.GOALKEEPER.value:
        return round(0.5 * player.overall)

    multiplier = 1 if player.preferred_position in position.value else 0.75
    return round(multiplier * player.overall)
