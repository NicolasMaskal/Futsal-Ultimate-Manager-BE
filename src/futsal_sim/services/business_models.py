# Inheriting from str because class needs to be json serializable
from enum import Enum


class TeamSheetPosition(str, Enum):
    RIGHT_ATTACKER = "right_attacker"
    LEFT_ATTACKER = "left_attacker"
    RIGHT_DEFENDER = "right_defender"
    LEFT_DEFENDER = "left_defender"
    GOALKEEPER = "goalkeeper"

    def __str__(self) -> str:
        return self.value
