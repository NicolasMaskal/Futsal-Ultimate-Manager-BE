from typing import Any

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.models import Player
from src.futsal_sim.serializers import (
    TeamSheetOutputSerializer,
    TeamSheetShortOutputSerializer,
)
from src.futsal_sim.services.team_service import TeamCRUDService
from src.futsal_sim.services.teamsheet_service import TeamSheetCRUDService


class TeamSheetCRUDApi(ApiAuthMixin, ViewSet):
    @staticmethod
    def _create_input_serializer(*, data: dict[str, Any], team_pk: str) -> serializers.Serializer:
        class InputSerializer(serializers.Serializer):
            right_attacker = serializers.PrimaryKeyRelatedField(queryset=Player.objects.filter(team_id=team_pk))
            left_attacker = serializers.PrimaryKeyRelatedField(queryset=Player.objects.filter(team_id=team_pk))
            right_defender = serializers.PrimaryKeyRelatedField(queryset=Player.objects.filter(team_id=team_pk))
            left_defender = serializers.PrimaryKeyRelatedField(queryset=Player.objects.filter(team_id=team_pk))
            goalkeeper = serializers.PrimaryKeyRelatedField(queryset=Player.objects.filter(team_id=team_pk))

        return InputSerializer(data=data)

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, allow_null=True, default=None)

    def retrieve(self, request: Request, pk: str, team_pk: str):
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        team_sheet = TeamSheetCRUDService(team=team).teamsheet_retrieve(teamsheet_id=int(pk))
        output_serializer = TeamSheetOutputSerializer(team_sheet)

        return Response(data=output_serializer.data)

    def list(self, request: Request, team_pk: str):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        queryset = TeamSheetCRUDService(team=team).teamsheet_list()
        serializer = TeamSheetShortOutputSerializer(queryset, many=True)

        return Response(data=serializer.data)

    def update(self, request: Request, pk: str, team_pk: str):
        serializer = self._create_input_serializer(data=request.data, team_pk=team_pk)
        serializer.is_valid(raise_exception=True)

        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        teamsheet = TeamSheetCRUDService(team=team).teamsheet_update(teamsheet_id=int(pk), **request.data)

        serializer_output = TeamSheetOutputSerializer(teamsheet)

        return Response(data=serializer_output.data)

    def create(self, request: Request, team_pk: str):
        serializer = self._create_input_serializer(data=request.data, team_pk=team_pk)
        serializer.is_valid(raise_exception=True)

        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        teamsheet = TeamSheetCRUDService(team=team).teamsheet_create(**request.data)

        serializer_output = TeamSheetOutputSerializer(teamsheet)

        return Response(data=serializer_output.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: str, team_pk: str):
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        TeamSheetCRUDService(team=team).teamsheet_delete(teamsheet_id=int(pk))

        return Response(status=status.HTTP_204_NO_CONTENT)
