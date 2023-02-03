from django.urls import path

from .apis import ActivateEmailAPI, UserListApi

urlpatterns = [
    path("", UserListApi.as_view(), name="list"),
    path("activate/<uidb64>/<token>/", ActivateEmailAPI.as_view(), name="activate"),
]
