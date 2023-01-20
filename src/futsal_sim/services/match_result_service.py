from django.db.models import Q, QuerySet

from src.common.utils import find_or_fail
from src.futsal_sim.models import MatchResult, Team
from src.users.models import User


class MatchResultReadService:
    def __init__(self, team: Team, user: User):
        self.team = team
        self.user = user

    def query_set(self) -> QuerySet[MatchResult]:
        """
        User can only view matches for teams they own.
        :return:
        """
        return MatchResult.objects.filter(
            Q(player_team=self.team) | Q(cpu_team=self.team, player_team__owner=self.user)
        )

    def match_list(self) -> QuerySet[MatchResult]:
        return self.query_set()

    def match_retrieve(self, match_id: int) -> QuerySet[MatchResult]:
        self.query_set()
        return find_or_fail(self.query_set(), error_message=f"Match result with id={match_id} not found!", id=match_id)
