from django.conf import settings
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import MinLengthValidator
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebTokenView

from src.api.mixins import ApiAuthMixin, CsrfExemptedSessionAuthentication
from src.authentication.services import auth_logout
from src.users.serializers import UserOutputSerializer
from src.users.services import user_create


class UserJwtRegisterApi(CsrfExemptedSessionAuthentication, APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(
            validators=[
                ASCIIUsernameValidator(),
                MinLengthValidator(6),
            ]
        )

    class OutputSerializer(serializers.Serializer):
        user = UserOutputSerializer()

    def post(self, request: Request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_create(email=serializer.data["email"], password=serializer.data["password"])
        serializer_output = UserOutputSerializer(user)
        return Response(serializer_output.data, status=status.HTTP_201_CREATED)


class UserJwtLoginApi(ObtainJSONWebTokenView):
    pass


class UserJwtLogoutApi(ApiAuthMixin, APIView):
    def post(self, request):
        auth_logout(request.user)

        response = Response()

        if settings.JWT_AUTH["JWT_AUTH_COOKIE"] is not None:
            response.delete_cookie(settings.JWT_AUTH["JWT_AUTH_COOKIE"])

        return response


class UserMeApi(ApiAuthMixin, APIView):
    def get(self, request):
        serializer = UserOutputSerializer(request.user)

        return Response(serializer.data)
