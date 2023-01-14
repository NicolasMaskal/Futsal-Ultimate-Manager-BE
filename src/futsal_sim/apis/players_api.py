from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.serializers import PlayerOutputSerializer
from src.futsal_sim.services.player_service import PlayerReadService
from src.futsal_sim.services.team_service import TeamCRUDService


class PlayerListApi(ApiAuthMixin, APIView):
    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False, allow_null=True, default=None)

    def get(self, request: Request, team_id: int):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        team = TeamCRUDService(user=request.user).team_retrieve(team_id=team_id)
        service = PlayerReadService(user=request.user, team=team)
        queryset = service.player_list(filters=filters_serializer.validated_data)
        serializer = PlayerOutputSerializer(queryset, many=True)

        return Response(data=serializer.data)
