from rest_framework import viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from futsal_sim.serializers import (
    PlayerSerializer,
    TeamSerializer,
    TeamSheetSerializer,
    SignupSerializer,
    MatchResultSerializer,
)
from .models import Player, Team, TeamSheet
from .apis.permissions import TeamPermission, OwnedByTeamPermission
from .services import team_service, pack_service


def create_error_response(e: Exception) -> Response:
    return Response({"error": True, "detail": str(e)}, status=400)


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

    @action(
        detail=True,
        methods=["post"],
        name="Play a match against the ai",
        permission_classes=[TeamPermission],
    )
    def play_match_ai(self, request, pk=None):
        try:
            team = self.get_object()  # So a permission error can be brought up
            team_service.validate_squad_size(team)
            difficulty = request.data["difficulty"]
            team_sheet_pk = request.data["player_team_sheet"]
            team_sheet = TeamSheet.objects.get(id=team_sheet_pk)
            team_service.validate_teamsheet_team(team, team_sheet)

            match_result = team_service.play_match_against_cpu(team_sheet, difficulty)
            return Response(match_result)
        except Exception as e:
            return create_error_response(e)

    @action(detail=True, methods=["get"], name="List match results of a team")
    def match_results(self, request, pk):
        team = self.get_object()  # So a permission error can be brought up
        results = team_service.get_match_results(team)
        data = [MatchResultSerializer().to_representation(r) for r in results]
        return Response(data)

    @action(detail=True, methods=["post"], name="Buy a pack")
    def buy_pack(self, request, pk):
        try:
            team = self.get_object()  # So a permission error can be brought up
            team_service.validate_squad_size(team)
            pack_type = request.data["pack_type"]
            players = pack_service.buy_pack(team, pack_type)
            pack_content = [PlayerSerializer().to_representation(p) for p in players]
        except Exception as e:
            return create_error_response(e)

        return Response(pack_content)

    @action(detail=True, methods=["post"], name="Sell players")
    def sell_players(self, request, pk):
        try:
            team = self.get_object()  # So a permission error can be brought up
            players = request.data["players"]
            team_service.sell_players(team, players)
        except Exception as e:
            return create_error_response(e)

        return Response({})

    @action(detail=False, methods=["get"], name="Get My Team")
    def my_team(self, request):
        try:
            team = Team.objects.get(owner=request.user)
        except Exception as e:
            return create_error_response(e)

        return Response(self.serializer_class().to_representation(team))


class TeamSheetViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSheetSerializer
    filterset_fields = ["team"]

    def get_permissions(self):
        return [OwnedByTeamPermission()]

    def get_queryset(self):
        if self.request.user and self.request.user.is_superuser:
            return TeamSheet.objects.all()
        user = self.request.user
        teams = Team.objects.filter(owner=user)
        return TeamSheet.objects.filter(team__in=teams)

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer_class = self.serializer_class(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

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


class SignupViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer


class LoginView(ObtainAuthToken):
    pass
    # def post(self, request, *args, **kwargs):
    #     try:
    #         response = super().post(request, *args, **kwargs)
    #     except Exception as e:
    #         return create_error_response(e.args[0]["non_field_errors"][0])
    #
    #     token = Token.objects.get(key=response.data["token"])
    #     user_id = token.user_id
    #     try:
    #         team = Team.objects.get(owner_id=user_id)
    #         response.data["team"] = model_to_dict(team)
    #     except ObjectDoesNotExist:
    #         response.data["team"] = None
    #     return response
