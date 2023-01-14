from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.serializers import PlayerOutputSerializer
from src.futsal_sim.services import pack_service
from src.futsal_sim.services.team_service import TeamCRUDService


# View is nested in team/<pk> resource
class TeamBuyPackApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        pack_type = serializers.ChoiceField(choices=["gold", "silver", "bronze"])

    def post(self, request: Request, pk: str):
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(pk))
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        players = pack_service.buy_pack(team=team, pack_type=serializer.data["pack_type"])
        output_serializer = PlayerOutputSerializer(players, many=True)
        return Response(output_serializer.data)
