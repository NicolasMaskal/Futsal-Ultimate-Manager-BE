import dataclasses
from dataclasses import dataclass
import random
import players.models as models
from typing import List, Optional
from enum import Enum


class TeamSheetPosition(Enum):
    RIGHT_ATTACKER = "right_attacker"
    LEFT_ATTACKER = "left_attacker"
    RIGHT_DEFENDER = "right_defender"
    LEFT_DEFENDER = "left_defender"
    GOALKEEPER = "goalkeeper"


class PositionManager:
    positions = [position for position in TeamSheetPosition]

    @staticmethod
    def generate_goal_scorer_position() -> TeamSheetPosition:
        return PositionManager.generate_position(
            attacker_perc=72, defender_perc=26, goalkeeper_perc=2
        )

    @staticmethod
    def generate_assist_maker_position() -> Optional[TeamSheetPosition]:
        assist_made = random.choice([True, False])
        if assist_made:
            return PositionManager.generate_position(
                attacker_perc=56, defender_perc=40, goalkeeper_perc=4
            )
        return None

    @staticmethod
    def generate_position(
        attacker_perc: int, defender_perc: int, goalkeeper_perc: int
    ) -> TeamSheetPosition:
        if attacker_perc + defender_perc + goalkeeper_perc != 100:
            raise ValueError("Percentages don't add up to 100!")

        seed = random.randint(1, 100)
        side_seed = random.randint(0, 1)
        if seed < attacker_perc:
            return PositionManager.positions[side_seed]
        elif seed < defender_perc + attacker_perc:
            return PositionManager.positions[2 + side_seed]  # First two positions are attackers
        else:
            return TeamSheetPosition.GOALKEEPER


class TeamSheetManager:
    def __init__(self, team_sheet):
        self.team_sheet = team_sheet

    def generate_scorer_update(self) -> TeamSheetPosition:
        """
        :return: Position of scorer
        """
        position = PositionManager.generate_goal_scorer_position()
        player = getattr(self.team_sheet, position.value)
        player.goals_scored += 1
        return position

    def generate_assister_update(self, scorer_position: TeamSheetPosition) -> Optional[TeamSheetPosition]:
        position = PositionManager.generate_assist_maker_position()
        while position == scorer_position:
            position = PositionManager.generate_assist_maker_position()

        if position:
            player = getattr(self.team_sheet, position.value)
            player.assists_made += 1
        return position

    def update_stamina(self):
        for position in PositionManager.positions:
            player = getattr(self.team_sheet, position.value)
            stamina_drained = random.randint(27, 33)
            if position == TeamSheetPosition.GOALKEEPER:
                # Goalkeepers aren't as tired as other positions
                stamina_drained = round(0.5 * stamina_drained)

            new_stamina = player.stamina_left - stamina_drained
            new_stamina = min(100, new_stamina)
            player.stamina_left = max(1, new_stamina)

    def match_finished(self):
        # self.update_stamina() Not for now
        for position in PositionManager.positions:
            player = getattr(self.team_sheet, position.value)
            player.matches_played += 1
            player.save()

    def get_team(self):
        return self.team_sheet.team


@dataclass
class MatchResult:
    player_goals: int
    cpu_goals: int
    player_goals_minutes: List[int]
    cpu_goals_minutes: List[int]
    player_goal_scorers: List[TeamSheetPosition]
    player_assist_makers: List[Optional[TeamSheetPosition]]


@dataclass
class _Match:
    home_average: int
    away_average: int
    team_sheet_manager: TeamSheetManager
    player_goals: int = 0
    cpu_goals: int = 0
    home_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    away_goals_minutes: List[int] = dataclasses.field(default_factory=lambda: [])
    player_goal_scorers: List[TeamSheetPosition] = dataclasses.field(default_factory=lambda: [])
    player_assist_makers: List[Optional[TeamSheetPosition]] = dataclasses.field(
        default_factory=lambda: []
    )

    def play_match(self) -> MatchResult:
        # using min so that lower scores are more common
        goal_amount = min(random.randint(1, 12) for _ in range(3))
        for i in range(goal_amount):
            self._add_goal_to_score()

        return self._create_match_result_from_score()

    def _create_match_result_from_score(self) -> MatchResult:
        self.home_goals_minutes.sort()
        self.away_goals_minutes.sort()

        models.MatchResult(
            player_score=self.player_goals,
            cpu_score=self.cpu_goals,
            cpu_average_overall=self.away_average,
            player_team=self.team_sheet_manager.get_team()
        ).save()
        player_goal_scorers_str = [scorer.value for scorer in self.player_goal_scorers]
        player_assist_makers_str = [assister.value for assister in self.player_assist_makers]
        self.team_sheet_manager.match_finished()

        return MatchResult(
            player_goals=self.player_goals,
            cpu_goals=self.cpu_goals,
            player_goals_minutes=self.home_goals_minutes,
            cpu_goals_minutes=self.away_goals_minutes,
            player_goal_scorers=player_goal_scorers_str,
            player_assist_makers=player_assist_makers_str,
        )

    def _add_goal_to_score(self):
        player_goal_chance = 50 + round(self.home_average - self.away_average)

        seed = random.randint(1, 100)
        if seed < player_goal_chance:
            self._add_player_goal()
        else:
            self._add_cpu_goal()

    def _add_player_goal(self):
        scorer_pos = self.team_sheet_manager.generate_scorer_update()
        self.player_goal_scorers.append(scorer_pos)

        assister_pos = self.team_sheet_manager.generate_assister_update(scorer_pos)
        if assister_pos:
            self.player_assist_makers.append(assister_pos)

        self.player_goals += 1
        time_of_goal = self.generate_random_minute()
        self.home_goals_minutes.append(time_of_goal)

    def _add_cpu_goal(self):
        self.cpu_goals += 1
        time_of_goal = self.generate_random_minute()
        self.away_goals_minutes.append(time_of_goal)

    def generate_random_minute(self) -> int:
        random_minute = random.randint(1, 90)
        while random_minute in self.home_goals_minutes + self.away_goals_minutes:
            random_minute = random.randint(1, 90)
        return random_minute


def get_team_average_overall(team_sheet, stamina_effect: bool = False) -> int:
    player_amount = 0
    ovr_total = 0

    for position in TeamSheetPosition:
        player = getattr(team_sheet, position.value)
        if player:
            player_amount += 1
            ovr_total += get_player_ovr_in_position(player, position, stamina_effect)

    return round(ovr_total / player_amount) if player_amount != 0 else 0


def get_player_ovr_in_position(
    player, position: TeamSheetPosition, stamina_effect: bool = False
) -> int:
    stamina_multiplier = player.stamina_left / 100 if stamina_effect else 1
    player_overall = round(stamina_multiplier * player.overall)
    if position == TeamSheetPosition.GOALKEEPER:
        return (
            player_overall if player.preferred_position == TeamSheetPosition.GOALKEEPER.value else 1
        )
    if player.preferred_position == models.PlayerPosition.GOALKEEPER.value:
        return round(0.5 * player_overall)

    multiplier = 1 if player.preferred_position in position.value else 0.75
    return round(multiplier * player_overall)


def play_match_against_cpu(player_team_sheet, cpu_average_overall) -> dict:
    if type(cpu_average_overall) != int or cpu_average_overall not in range(1, 100):
        raise ValueError("Average overall has to be a number between 1 and 100!")
    player_average = get_team_average_overall(player_team_sheet, stamina_effect=True)
    team_sheet_manager = TeamSheetManager(player_team_sheet)
    match = _Match(player_average, cpu_average_overall, team_sheet_manager)
    match_result = match.play_match()
    return dataclasses.asdict(match_result)
