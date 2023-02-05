from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import MinLengthValidator
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebTokenView

from src.api.mixins import ApiAuthMixin
from src.authentication.serializers import PasswordField
from src.authentication.services import activate_email, auth_logout
from src.futsal_sim.services.team_service import TeamCRUDService
from src.futsal_sim.services.teamsheet_service import TeamSheetCRUDService
from src.users.serializers import UserOutputSerializer
from src.users.services import user_create, user_change_password


class UserSessionLoginApi(APIView):
    """
    Following https://docs.djangoproject.com/en/3.1/topics/auth/default/#how-to-log-a-user-in
    """

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = PasswordField()

    def post(self, request: Request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request, **serializer.validated_data)

        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        output_serializer = UserOutputSerializer(user)
        session_key = request.session.session_key

        return Response({"session": session_key, "user": output_serializer.data})


class UserSessionLogoutApi(APIView):
    def post(self, request):
        logout(request)

        return Response()


class UserRegisterApi(APIView):
    class InputSerializer(serializers.Serializer):
        team_name = serializers.CharField()
        email = serializers.EmailField()
        password = serializers.CharField(
            validators=[
                ASCIIUsernameValidator(),
                MinLengthValidator(6),
            ]
        )

    def post(self, request: Request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_create(
            email=serializer.data["email"], password=serializer.data["password"], is_admin=False, email_verified=False
        )
        activate_email(domain=str(get_current_site(request).domain), use_https=request.is_secure(), user=user)
        team = TeamCRUDService(user=user).team_create(name=serializer.data["team_name"])
        TeamSheetCRUDService(team=team).teamsheet_create(name="Teamsheet")
        login(request, user)
        output_serializer = UserOutputSerializer(user)

        return Response(
            {"message": "Account awaiting email verification!", "user": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class UserChangePassword(ApiAuthMixin, APIView):
    class InputSerializer(serializers.Serializer):
        password = PasswordField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        user_change_password(user=request.user, password=serializer.data["password"])
        return Response({"message": "Password successfully changed!"})


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
