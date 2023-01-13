from django.urls import path, include

from src.futsal_sim.apis.players_api import PlayerListApi
from src.futsal_sim.apis.teams_api import TeamCreateApi

urlpatterns = [
    path("players/", PlayerListApi.as_view(), name="players"),
    path("teams/", TeamCreateApi.as_view(), name="teams")
]
