from django.urls import path

from .apis import UserJwtLoginApi, UserJwtLogoutApi, UserJwtRegisterApi, UserMeApi

urlpatterns = [
    path("register/", UserJwtRegisterApi.as_view(), name="register"),
    path("login/", UserJwtLoginApi.as_view(), name="login"),
    path("logout/", UserJwtLogoutApi.as_view(), name="logout"),
    path("me/", UserMeApi.as_view(), name="me"),
]
