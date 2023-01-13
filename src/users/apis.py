from rest_framework import serializers
from rest_framework.views import APIView

from src.api.pagination import (
    LimitOffsetPagination,
    get_paginated_response,
)
from src.users.selectors import user_list
from src.users.serializers import UserOutputSerializer


class UserListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        is_admin = serializers.BooleanField(required=False, allow_null=True, default=None)
        email = serializers.EmailField(required=False)

    def get(self, request):
        # Make sure the filters are valid, if passed
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        users = user_list(filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=UserOutputSerializer,
            queryset=users,
            request=request,
            view=self,
        )