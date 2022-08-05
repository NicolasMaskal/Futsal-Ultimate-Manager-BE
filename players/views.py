from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .permissions import TeamPermission, OwnedByTeamPermission
from .models import Player, Team, TeamSheet, Token, MatchResult
from .serializers import PlayerSerializer, TeamSerializer, TeamSheetSerializer, SignupSerializer, MatchResultSerializer
from .services import team_service
from django.contrib.auth.models import User


def create_error_response(e: Exception) -> Response:
    return Response({"error": True, "detail": str(e)}, status=400)


class PlayerViewSet(viewsets.ModelViewSet):  # TODO Change so that only list is ok
    serializer_class = PlayerSerializer
    filterset_fields = ['team']

    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            return Player.objects.all()
        user = self.request.user
        teams = Team.objects.filter(owner=user)
        return Player.objects.filter(team__in=teams)

    def get_permissions(self):
        return [OwnedByTeamPermission()]


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            return Team.objects.all()
        user = self.request.user
        return Team.objects.filter(owner=user)

    def get_permissions(self):
        return [TeamPermission()]

    @action(detail=True, methods=["post"], name="Play a match against the ai", permission_classes=[TeamPermission])
    def play_match_ai(self, request, pk=None):
        try:
            # TODO move validation to serializer?
            team = self.get_object()  # So a permission error can be brought up
            difficulty = request.data["difficulty"]
            team_sheet_pk = request.data["player_team_sheet"]
            team_sheet = TeamSheet.objects.get(id=team_sheet_pk)

            if team != team_sheet.team:
                raise ValueError(
                    f"Team_sheet({team_sheet_pk}) doesn't belong to team({team_sheet.team.id})!"
                )
            match_result = team_service.play_match_against_cpu(team_sheet, difficulty)
            return Response(match_result)
        except Exception as e:
            return create_error_response(e)

    @action(detail=True, methods=["get"], name="List match results of a team")
    def match_results(self, request, pk):
        team = self.get_object()  # So a permission error can be brought up
        match_results = MatchResult.objects.filter(player_team=team)
        data = []
        result_serializer = MatchResultSerializer()
        for match_result in match_results:
            json_repr = result_serializer.to_representation(match_result)
            data.append(json_repr)

        return Response(data)


class TeamSheetViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSheetSerializer
    filterset_fields = ['team']
    # TODO Add match results

    def get_permissions(self):
        return [OwnedByTeamPermission()]

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer_class = self.serializer_class(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            return TeamSheet.objects.all()
        user = self.request.user
        teams = Team.objects.filter(owner=user)
        return TeamSheet.objects.filter(team__in=teams)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.team.id != request.data["team"]:
                raise ValueError("Cannot change team of TeamSheet!")

            serializer_class = self.serializer_class(data=request.data)
            serializer_class.is_valid(raise_exception=True)
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return create_error_response(e)


class SignupViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        data = super().create(request, *args, **kwargs).data
        username = data["username"]
        user = User.objects.get(username=username)
        token = Token.objects.get(user=user)
        data["token"] = token.key
        return Response(data, status=201)