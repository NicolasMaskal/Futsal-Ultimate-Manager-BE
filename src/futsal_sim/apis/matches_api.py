from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from src.api.mixins import ApiAuthMixin
from src.futsal_sim.models import TeamSheet
from src.futsal_sim.serializers import (
    MatchResultOutputSerializer,
    MatchResultShortOutputSerializer,
)
from src.futsal_sim.services.match_result_service import MatchResultReadService
from src.futsal_sim.services.match_service import play_match_against_cpu
from src.futsal_sim.services.team_service import TeamCRUDService
from src.futsal_sim.services.teamsheet_service import (
    TeamSheetCRUDService,
    validate_teamsheet_can_play_match,
)

# View is nested in team/<pk> resource


class MatchApi(ApiAuthMixin, ViewSet):
    def create(self, request: Request, team_pk: str):
        class InputSerializer(serializers.Serializer):
            difficulty_rating = serializers.IntegerField(min_value=1, max_value=10)
            team_sheet = serializers.PrimaryKeyRelatedField(queryset=TeamSheet.objects.filter(team_id=team_pk))

        serializer = InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        team_sheet = TeamSheetCRUDService(team=team).teamsheet_retrieve(teamsheet_id=serializer.data["team_sheet"])

        validate_teamsheet_can_play_match(team_sheet)
        match_result = play_match_against_cpu(
            player_team_sheet=team_sheet, difficulty_rating=serializer.data["difficulty_rating"]
        )
        output_serializer = MatchResultOutputSerializer(match_result)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request: Request, team_pk: str):
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        matches = MatchResultReadService(team=team, user=request.user).match_list()
        serializer = MatchResultShortOutputSerializer(matches, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, team_pk: str, pk: str):
        team = TeamCRUDService(user=request.user).team_retrieve(team_id=int(team_pk))
        match = MatchResultReadService(team=team).match_retrieve(match_id=int(pk))
        serializer = MatchResultOutputSerializer(match)
        return Response(serializer.data)
