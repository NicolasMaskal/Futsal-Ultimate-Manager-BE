from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from players.views import PlayerViewSet, TeamViewSet, TeamSheetViewSet, SignupViewSet, LoginView

router = DefaultRouter()

router.register("players", PlayerViewSet, "players")
router.register("teams", TeamViewSet, "teams")
router.register("team-sheets", TeamSheetViewSet, "team-sheets")
router.register("auth/sign-up", SignupViewSet, "sign-up")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("auth/login/", LoginView.as_view()),
]
