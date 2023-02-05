from django.urls import include, path

from .apis import (
    UserChangePassword,
    UserJwtLoginApi,
    UserJwtLogoutApi,
    UserMeApi,
    UserRegisterApi,
    UserSessionLoginApi,
    UserSessionLogoutApi,
)

urlpatterns = [
    path("change-password/", UserChangePassword.as_view(), name="change-password"),
    path("me/", UserMeApi.as_view(), name="me"),
    path("register/", UserRegisterApi.as_view(), name="register"),
    path(
        "jwt/",
        include(
            (
                [
                    path("login/", UserJwtLoginApi.as_view(), name="login"),
                    path("logout/", UserJwtLogoutApi.as_view(), name="logout"),
                ],
                "jwt",
            )
        ),
    ),
    path(
        "session/",
        include(
            (
                [
                    path("login/", UserSessionLoginApi.as_view(), name="login"),
                    path("logout/", UserSessionLogoutApi.as_view(), name="logout"),
                ],
                "session",
            )
        ),
    ),
]
