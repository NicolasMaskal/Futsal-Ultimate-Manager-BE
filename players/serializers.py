from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers
from players.models import Player, Team, TeamSheet, MatchResult
from .services import team_service


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = "__all__"


class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Team
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["average_overall"] = team_service.get_team_average_overall(instance)

        players = Player.objects.filter(team=representation["id"]).all()
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
            if player.team != team:
                raise ValueError(f"Player {player} is not a player of team {player.team}")
        return data


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        validate_email(value)
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model()(**validated_data)

        user.set_password(validated_data['password'])
        user.save()
        return user