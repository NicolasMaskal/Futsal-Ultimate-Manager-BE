from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers

from futsal_sim.models import MatchResult, Player, Team, TeamSheet
from futsal_sim.services import player_service, team_service


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        team_avg = team_service.calc_team_average_skill(instance.team)
        representation["sell_price"] = player_service.get_player_sell_price(instance, team_avg)
        return representation


class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = "__all__"

    def to_representation(self, instance):
        # 2022-09-10T16:22:08.699685Z -> 10.09.2022

        representation = super().to_representation(instance)
        split_in_half = representation["date"].split("T")
        year, month, day = split_in_half[0].split("-")

        representation["date"] = f"{day}.{month}.{year}"
        return representation


class TeamSerializer(serializers.ModelSerializer):
    # So that owner isn't a required field when creating a team (is automatically set in perform_create)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Team
        fields = "__all__"

    def to_representation(self, instance: Team):
        representation = super().to_representation(instance)

        representation["average_skill"] = team_service.calc_team_average_skill(instance)
        players = Player.objects.filter(team=representation["id"]).all()
        representation["team_size"] = len(players)

        team_sheets = TeamSheet.objects.filter(team=representation["id"]).all()
        representation["team_sheets_amount"] = len(team_sheets)

        representation["valid_team_size"] = instance.has_valid_squad_size
        return representation


class TeamSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamSheet
        fields = "__all__"
        # read_only_fields = ('team',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["average_skill"] = team_service.get_teamsheet_average_skill(instance)
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
            if player.team != team:
                raise ValueError(f"Player {player} is not a player of team {player.team}")
        return data


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        validate_email(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model()(**validated_data)

        user.set_password(validated_data["password"])
        user.save()
        return user
