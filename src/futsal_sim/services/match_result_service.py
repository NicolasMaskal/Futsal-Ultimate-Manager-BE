from django.db.models import QuerySet

from src.common.utils import find_or_fail
from src.futsal_sim.models import Team, MatchResult


class MatchResultReadService:
    def __init__(self, team: Team):
        self.team = team

    def query_set(self) -> QuerySet[MatchResult]:
        return MatchResult.objects.filter(player_team=self.team)

    def match_list(self) -> QuerySet[MatchResult]:
        return self.query_set()

    def match_retrieve(self, match_id: int) -> QuerySet[MatchResult]:
        self.query_set()
        return find_or_fail(self.query_set(), error_message=f"Match result with id={match_id} not found!", id=match_id)
