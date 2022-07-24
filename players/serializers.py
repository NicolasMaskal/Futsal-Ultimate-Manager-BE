from rest_framework import serializers
from players.models import Player, Team, TeamSheet, PlayerTeamSheetLocation


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        players = Player.objects.filter(current_team=representation["id"]).all()
        representation["players"] = [player.id for player in players]

        team_sheets = TeamSheet.objects.filter(team=representation["id"]).all()
        representation["team_sheets"] = [team_sheet.id for team_sheet in team_sheets]
        return representation


class TeamSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamSheet
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        team_sheet_locs = PlayerTeamSheetLocation.objects.filter(team_sheet=representation["id"])
        representation["player_locations"] = [
            (team_sheet_loc.index, team_sheet_loc.player.id) for team_sheet_loc in team_sheet_locs
        ]
        return representation
