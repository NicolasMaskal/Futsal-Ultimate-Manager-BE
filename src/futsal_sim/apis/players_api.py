from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Player
from ..services.player_service import PlayerReadService
from ..services.team_service import calc_team_average_skill


class PlayerListApi(APIView):
    permission_classes = []

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.BooleanField(required=False, allow_null=True, default=None)
        team_id = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.ModelSerializer):
        sell_price = serializers.SerializerMethodField()

        def get_sell_price(self, obj: Player):
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

    def get(self, request: Request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        service = PlayerReadService(request.user)
        queryset = service.player_list(filters=filters_serializer.validated_data)
        serializer = self.OutputSerializer(queryset, many=True)

        return Response(data=serializer.data)
