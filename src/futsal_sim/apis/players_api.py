from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.futsal_sim.serializers import PlayerOutputSerializer
from src.futsal_sim.services.player_service import PlayerReadService


class PlayerListApi(APIView):
    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        name = serializers.CharField(required=False, allow_null=True, default=None)

    def get(self, request: Request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        service = PlayerReadService(user=request.user)
        queryset = service.player_list(filters=filters_serializer.validated_data)
        serializer = PlayerOutputSerializer(queryset, many=True)

        return Response(data=serializer.data)
