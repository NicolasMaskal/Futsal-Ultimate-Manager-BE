from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.api.pagination import LimitOffsetPagination, get_paginated_response
from src.users.models import User
from src.users.selectors import user_list
from src.users.serializers import UserOutputSerializer
from src.users.tokens import account_activation_token


class UserListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 1

    class FilterSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=False)
        is_admin = serializers.BooleanField(required=False, allow_null=True, default=None)
        email = serializers.EmailField(required=False)

    def get(self, request: Request):
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


class ActivateEmailAPI(APIView):
    def get(self, request: Request, uidb64: str, token: str):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.email_verified = True
            user.save()

            return Response({"message": "Thank you for your email confirmation. Now you can login your account."})
        else:
            raise ValueError("Activation link is invalid!")
