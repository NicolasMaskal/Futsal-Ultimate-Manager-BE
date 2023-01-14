from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ...api.mixins import ApiAuthMixin
from ..serializers import TeamOutputSerializer
from ..services.team_service import team_create


class TeamCreateApi(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_team = team_create(user=request.user, name=serializer.data["name"])

        serializer = TeamOutputSerializer(created_team)

        return Response(data=serializer.data, status=201)
