from django.urls import include, path

from .apis import (
    UserJwtLoginApi,
    UserJwtLogoutApi,
    UserMeApi,
    UserRegisterApi,
    UserSessionLoginApi,
    UserSessionLogoutApi,
)

urlpatterns = [
    path("register/", UserRegisterApi.as_view(), name="register"),
    path("login/", UserJwtLoginApi.as_view(), name="login"),
    path("logout/", UserJwtLogoutApi.as_view(), name="logout"),
    path("me/", UserMeApi.as_view(), name="me"),
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
