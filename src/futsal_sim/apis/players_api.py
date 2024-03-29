from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.constants import TEAM_SKILL_CALC_PLAYER_AMOUNT
from src.futsal_sim.serializers import PlayerOutputSerializer
from src.futsal_sim.services.player_service import PlayerReadService
from src.futsal_sim.services.team_service import (
    TeamCRUDService,
    calc_average_skill,
    calc_team_skill,
)

# View is nested in teams resource


class PlayerListApi(ApiAuthMixin, ViewSet):
    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False, allow_null=True, default=None)

    def list(self, request: Request, team_pk: str):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        service = PlayerReadService(user=request.user, team=team)
        queryset = service.player_list(filters=filters_serializer.validated_data)
        serializer = PlayerOutputSerializer(queryset, many=True)
        average_skill = calc_average_skill(team)
        team_skill = calc_team_skill(team)
        return Response(
            {
                "team_skill": team_skill,
                "average_skill": average_skill,
                "player_amount_considered": TEAM_SKILL_CALC_PLAYER_AMOUNT,
                "players": serializer.data,
            }
        )
