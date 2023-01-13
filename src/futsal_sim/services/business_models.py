# Inheriting from str because class needs to be json serializable
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TeamSheetPosition(str, Enum):
    RIGHT_ATTACKER = "right_attacker"
    LEFT_ATTACKER = "left_attacker"
    RIGHT_DEFENDER = "right_defender"
    LEFT_DEFENDER = "left_defender"
    GOALKEEPER = "goalkeeper"


@dataclass
class CpuTeamSheetNames:
    right_attacker: str
    left_attacker: str
    right_defender: str
    left_defender: str
    goalkeeper: str


@dataclass
class MatchResultOutput:
    coins_reward: int
    player_average_skill: int
    cpu_average_skill: int
    cpu_team_name: str
    player_goals: int
    cpu_goals: int
    player_goals_minutes: list[int]
    cpu_goals_minutes: list[int]
    player_goal_scorers: list[TeamSheetPosition]
    cpu_goal_scorers: list[TeamSheetPosition]
    player_assist_makers: list[Optional[TeamSheetPosition]]
    cpu_assist_makers: list[Optional[TeamSheetPosition]]
    cpu_team_sheet: CpuTeamSheetNames
