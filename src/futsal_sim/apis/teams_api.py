from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.serializers import TeamOutputSerializer
from src.futsal_sim.services.team_service import TeamCRUDService


class TeamCRUDApi(ApiAuthMixin, ViewSet):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField()

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False, allow_null=True, default=None)

    def retrieve(self, request: Request, pk: str):
        service = TeamCRUDService(user=request.user)
        team = service.team_retrieve(team_id=int(pk))
        serializer = TeamOutputSerializer(team)

        return Response(data=serializer.data)

    def list(self, request: Request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        service = TeamCRUDService(user=request.user)
        queryset = service.team_list(filters=filters_serializer.validated_data)
        serializer = TeamOutputSerializer(queryset, many=True)

        return Response(data=serializer.data)

    def put(self, request: Request, pk: int):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = TeamCRUDService(user=request.user)
        created_team = service.team_update(team_id=pk, name=serializer.data["name"])

        serializer_output = TeamOutputSerializer(created_team)

        return Response(data=serializer_output.data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = TeamCRUDService(user=request.user)
        created_team = service.team_create(name=serializer.data["name"])

        serializer_output = TeamOutputSerializer(created_team)

        return Response(data=serializer_output.data, status=status.HTTP_201_CREATED)

    def delete(self, request: Request, pk: str):
        service = TeamCRUDService(user=request.user)
        service.team_delete(team_id=int(pk))

        return Response(status=status.HTTP_204_NO_CONTENT)
