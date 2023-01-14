from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet

from src.futsal_sim.constants import (
    MULTIPLIER_DIFFERENT_INFIELD_POS,
    MULTIPLIER_GK_INFIELD,
    MULTIPLIER_INFIELD_AS_GK,
    MULTIPLIER_PLAYER_FAV_POS,
    STAMINA_EFFECT,
)
from src.futsal_sim.filters import PlayerFilter
from src.futsal_sim.models import Player, Team
from src.futsal_sim.services.business_models import TeamSheetPosition
from src.users.models import User


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


class PlayerSkillCalculator:
    def __init__(self, *, player: Player, cur_pos: TeamSheetPosition):
        self.player = player
        self.cur_pos = cur_pos
        self._res_skill: Optional[int] = None

    def _playing_in_fav_pos(self) -> bool:
        return self.player.preferred_position in self.cur_pos.value

    def _apply_multiplier(self, multiplier: float):
        if not self._res_skill:
            raise ValueError("Programming error, res_skill is None!")
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

        if self._res_skill is None:
            raise ValueError("Result skill is none!")

        return max(1, self._res_skill)