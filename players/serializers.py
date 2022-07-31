from rest_framework import serializers
from players.models import Player, Team, TeamSheet
from .services import team_service


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

        representation["average_overall"] = team_service.get_team_average_overall(instance)

        players = Player.objects.filter(current_team=representation["id"]).all()
        representation["players"] = [player.id for player in players]

        team_sheets = TeamSheet.objects.filter(team=representation["id"]).all()
        representation["team_sheets"] = [team_sheet.id for team_sheet in team_sheets]

        return representation


class TeamSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamSheet
        fields = "__all__"
        # read_only_fields = ('team',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["average_overall"] = team_service.get_teamsheet_average_overall(instance)
        return representation

    def validate(self, data):
        positions = [
            "right_attacker",
            "left_attacker",
            "right_defender",
            "left_defender",
            "goalkeeper",
        ]
        players = [data[position] for position in positions if data[position] is not None]

        if len(set(players)) != len(players):
            raise ValueError("One player is playing in more than one position")

        team = data["team"]
        for player in players:
            if player.current_team != team:
                raise ValueError(f"Player {player} is not a player of team {player.current_team}")
        return data
