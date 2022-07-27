import json

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player, Team, TeamSheet
from .serializers import PlayerSerializer, TeamSerializer, TeamSheetSerializer
from .services import play_match_against_ai


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @action(detail=True, methods=["post"], name="Play a match against the ai")
    def play_match_ai(self, request, pk=None):
        ai_average_overall = request.data["ai_average_overall"]
        team_sheet_pk = request.data["player_team_sheet"]
        team_sheet = TeamSheet.objects.get(id=team_sheet_pk)
        if int(pk) != team_sheet.team.id:
            raise ValueError(
                f"Team_sheet({team_sheet_pk}) doesn't belong to team({team_sheet.team.id})!"
            )
        match_result = play_match_against_ai(team_sheet, ai_average_overall)
        return Response(match_result)


class TeamSheetViewSet(viewsets.ModelViewSet):
    queryset = TeamSheet.objects.all()
    serializer_class = TeamSheetSerializer

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
            return Response({"error": True, "detail": str(e)}, status=400)
