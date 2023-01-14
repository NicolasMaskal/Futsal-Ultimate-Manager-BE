from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.serializers import TeamOutputSerializer
from src.futsal_sim.services.team_service import team_create


class TeamCreateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_team = team_create(user=request.user, name=serializer.data["name"])

        serializer_output = TeamOutputSerializer(created_team)

        return Response(data=serializer_output.data, status=201)
