import random
from typing import Optional

import names
from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet

from .. import models
from ..constants import (
    MULTIPLIER_PLAYER_FAV_POS,
    MULTIPLIER_GK_INFIELD,
    MULTIPLIER_DIFFERENT_INFIELD_POS,
    MULTIPLIER_INFIELD_AS_GK, STAMINA_EFFECT,
)
from ..filters import PlayerFilter
from ..models import PlayerPosition, Player, Team
from .business_models import TeamSheetPosition
from ...users.models import User


class PlayerReadService:
    # TODO rewrite
    def __init__(self, user: User):
        self.user = user

    def query_set(self) -> QuerySet[Player]:
        if isinstance(self.user, AnonymousUser) or self.user.is_admin:
            return Player.objects.all()
        else:
            teams = Team.objects.filter(owner=self.user)
            return Player.objects.filter(team__in=teams)

    def player_list(self, *, filters=None) -> QuerySet[Player]:
        filters = filters or {}
        qs = self.query_set()
        return PlayerFilter(filters, qs).qs

    def player_get(self, *, player_id: int) -> Player:
        return self.query_set().get(player_id)


class PlayerGenerator:
    def __init__(self, *, team: Team, lower_end: int, upper_end: int):
        self.team = team
        self.lower_end = lower_end
        self.upper_end = upper_end

    def generate_players(self, amount: int) -> list[Player]:
        players = []
        for _ in range(amount):
            player = self.generate_player()
            players.append(player)
        return players

    def generate_player(self):
        player_name = self.generate_random_name()
        player_position = self._generate_random_pos()
        player_skill = self._generate_random_skill()
        player = models.Player(
            name=player_name,
            preferred_position=player_position,
            team=self.team,
            skill=player_skill,
        )
        player.save()

        return player

    def _generate_random_skill(self) -> int:
        return random.randint(self.lower_end, self.upper_end)

    @staticmethod
    def _generate_random_pos() -> str:
        seed = random.randint(1, 100)
        if seed <= 20:
            return PlayerPosition.GOALKEEPER
        if seed <= 60:
            return PlayerPosition.DEFENDER
        return PlayerPosition.ATTACKER

    @staticmethod
    def generate_random_name() -> str:
        return names.get_full_name(gender="male")


class PlayerSkillCalculator:
    def __init__(self, *, player: Player, cur_pos: TeamSheetPosition):
        self.player = player
        self.cur_pos = cur_pos
        self._res_skill: Optional[int] = None

    def _playing_in_fav_pos(self) -> bool:
        return self.player.preferred_position in self.cur_pos.value

    def _apply_multiplier(self, multiplier: float):
        self._res_skill = round(multiplier * self._res_skill)

    def _apply_stamina_effect(self):
        multiplier = self.player.stamina_left / 100
        self._apply_multiplier(multiplier)

    def _apply_playing_as_gk(self):
        multiplier = MULTIPLIER_INFIELD_AS_GK
        if self._playing_in_fav_pos():
            multiplier = MULTIPLIER_PLAYER_FAV_POS
        self._apply_multiplier(multiplier)

    def _apply_playing_infield(self):
        if self.player.is_gk():
            multiplier = MULTIPLIER_GK_INFIELD
        elif self._playing_in_fav_pos():
            multiplier = 1
        else:
            multiplier = MULTIPLIER_DIFFERENT_INFIELD_POS
        self._apply_multiplier(multiplier)

    def calc_skill_in_pos(self) -> int:
        self._res_skill = self.player.skill

        if STAMINA_EFFECT:
            self._apply_stamina_effect()

        if self.cur_pos == TeamSheetPosition.GOALKEEPER:
            self._apply_playing_as_gk()
        else:
            self._apply_playing_infield()

        return max(1, self._res_skill)
