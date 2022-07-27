import dataclasses
from dataclasses import dataclass
import random
from .models import PlayerPosition
from typing import List


@dataclass
class Match:
    home_average: int
    away_average: int
    home_goals: int = 0
    away_goals: int = 0
    home_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    away_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])

    def play_match(self):
        # using min so that lower scores are more common
        goal_amount = min(random.randint(1, 12) for _ in range(3))
        for i in range(goal_amount):
            self._add_goal_to_score()

        self.home_goals_minutes.sort()
        self.away_goals_minutes.sort()

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


def play_match_against_ai(player_team_sheet, ai_average_overall: int) -> dict:
    player_average = get_team_average_overall(player_team_sheet)
    match = Match(player_average, ai_average_overall)
    match.play_match()
    return dataclasses.asdict(match)


def get_team_average_overall(team_sheet) -> int:
    positions = ["right_attacker", "left_attacker", "right_defender", "left_defender", "goalkeeper"]
    player_amount = 0
    ovr_total = 0

    for position in positions:
        player = getattr(team_sheet, position)
        if player:
            player_amount += 1
            ovr_total += get_player_ovr_in_position(player, position)

    return round(ovr_total / player_amount) if player_amount != 0 else 0


def get_player_ovr_in_position(player, position) -> int:
    if position == PlayerPosition.GOALKEEPER:
        return player.overall if player.preferred_position == position else 1
    if player.preferred_position == PlayerPosition.GOALKEEPER:
        return round(0.5 * player.overall)

    multiplier = 1 if player.preferred_position in position else 0.75
    return round(multiplier * player.overall)
