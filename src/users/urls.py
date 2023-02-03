from django.urls import path

from . import apis
from .apis import UserListApi, ActivateEmailAPI

urlpatterns = [
    path("", UserListApi.as_view(), name="list"),
    path("activate/<uidb64>/<token>/", ActivateEmailAPI.as_view(), name="activate"),
]
