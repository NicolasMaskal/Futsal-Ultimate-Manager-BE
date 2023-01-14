from rest_framework import serializers

from src.futsal_sim.models import Player, Team
from src.futsal_sim.services.team_service import calc_team_average_skill


class TeamOutputSerializer(serializers.ModelSerializer):
    player_amount = serializers.SerializerMethodField()

    def get_player_amount(self, obj: Team) -> int:
        return obj.players.count()

    class Meta:
        model = Team
        fields = ("id", "name", "wins", "draws", "loses", "coins", "has_valid_squad_size", "player_amount")


class PlayerOutputSerializer(serializers.ModelSerializer):
    sell_price = serializers.SerializerMethodField()

    def get_sell_price(self, obj: Player) -> int:
        team_avg = calc_team_average_skill(obj.team)
        return obj.calc_sell_price(team_avg)

    class Meta:
        model = Player
        fields = (
            "id",
            "name",
            "preferred_position",
            "skill",
            "stamina_left",
            "matches_played",
            "goals_scored",
            "assists_made",
            "team_id",
            "sell_price",
        )
