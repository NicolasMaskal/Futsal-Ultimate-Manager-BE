from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from players.views import PlayerViewSet, TeamViewSet, TeamSheetViewSet

router = DefaultRouter()

router.register("players", PlayerViewSet, "players")
router.register("teams", TeamViewSet, "teams")
router.register("team-sheets", TeamSheetViewSet, "nations")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
]
