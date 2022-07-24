from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player, Team, TeamSheet, PlayerTeamSheetLocation
from .serializers import PlayerSerializer, TeamSerializer, TeamSheetSerializer
from .services import play_match_against_ai


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @action(detail=False, methods=["post"], name="Play a match against the ai")
    def play_match_ai(self, request, pk=None):
        ai_average_overall = request.data["ai_average_overall"]
        player_team_sheet = request.data["player_team_sheet"]
        match_result = play_match_against_ai(player_team_sheet, ai_average_overall)
        return Response({"Player": match_result.home_score, "Ai": match_result.away_score})


class TeamSheetViewSet(viewsets.ModelViewSet):
    queryset = TeamSheet.objects.all()
    serializer_class = TeamSheetSerializer

    def update(self, request, **kwargs):
        team_sheet = self.get_object()
        PlayerTeamSheetLocation.objects.filter(team_sheet=team_sheet.id).delete()

        player_locations = request.data["player_locations"]
        for index, player_id in player_locations:
            player = Player.objects.get(id=player_id)
            PlayerTeamSheetLocation.objects.create(
                player=player, index=index, team_sheet=team_sheet
            )
        return super().update(request, **kwargs)
