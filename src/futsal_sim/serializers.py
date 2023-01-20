from rest_framework import serializers

from src.futsal_sim.models import (
    MatchGoal,
    MatchResult,
    Player,
    Team,
    TeamLineup,
    TeamSheet,
)
from src.futsal_sim.services.team_service import calc_team_skill


class TeamOutputSerializer(serializers.ModelSerializer):
    player_amount = serializers.SerializerMethodField()

    def get_player_amount(self, obj: Team) -> int:
        return obj.players.count()

    class Meta:
        model = Team
        fields = ("id", "name", "wins", "draws", "loses", "coins", "player_amount")


class PlayerOutputSerializer(serializers.ModelSerializer):
    sell_price = serializers.SerializerMethodField()

    def get_sell_price(self, obj: Player) -> int:
        team_skill = calc_team_skill(obj.team)
        return obj.calc_sell_price(team_skill)

    class Meta:
        model = Player
        fields = (
            "id",
            "name",
            "preferred_position",
            "skill",
            "matches_played",
            "goals_scored",
            "assists_made",
            "sell_price",
        )


class TeamSheetOutputSerializer(serializers.ModelSerializer):
    right_attacker = PlayerOutputSerializer()
    left_attacker = PlayerOutputSerializer()
    right_defender = PlayerOutputSerializer()
    left_defender = PlayerOutputSerializer()
    goalkeeper = PlayerOutputSerializer()

    class Meta:
        model = TeamSheet
        fields = ("id", "name", "right_attacker", "left_attacker", "right_defender", "left_defender", "goalkeeper")


class TeamLineupOutputSerializer(serializers.ModelSerializer):
    right_attacker = PlayerOutputSerializer()
    left_attacker = PlayerOutputSerializer()
    right_defender = PlayerOutputSerializer()
    left_defender = PlayerOutputSerializer()
    goalkeeper = PlayerOutputSerializer()

    class Meta:
        model = TeamLineup
        fields = ("right_attacker", "left_attacker", "right_defender", "left_defender", "goalkeeper")


class TeamSheetShortOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamSheet
        fields = ("id", "name")


class MatchMomentOutputSerializer(serializers.ModelSerializer):
    goal_scorer = PlayerOutputSerializer()
    assister = PlayerOutputSerializer()

    class Meta:
        model = MatchGoal
        fields = ("minute", "goal_scorer", "assister")


class MatchResultOutputSerializer(serializers.ModelSerializer):
    player_team = TeamOutputSerializer()
    cpu_team = TeamOutputSerializer()
    player_lineup = TeamLineupOutputSerializer()
    cpu_lineup = TeamLineupOutputSerializer()
    goal_moments = MatchMomentOutputSerializer(many=True)

    class Meta:
        model = MatchResult
        fields = (
            "id",
            "date",
            "player_goals",
            "cpu_goals",
            "player_team",
            "cpu_team",
            "player_lineup",
            "cpu_lineup",
            "coins_reward",
            "goal_moments",
        )
