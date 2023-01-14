from django.urls import path
from rest_framework import routers

from src.futsal_sim.apis.packs_api import TeamBuyPackApi
from src.futsal_sim.apis.players_api import PlayerListApi
from src.futsal_sim.apis.teams_api import SellPlayersApi, TeamCRUDApi

router = routers.SimpleRouter()
router.register(r"teams", TeamCRUDApi, "teams")


urlpatterns = [
    path("players/", PlayerListApi.as_view(), name="players"),
    path("teams/<int:pk>/buy-pack/", TeamBuyPackApi.as_view(), name="team-buy-pack"),
    path("teams/<int:pk>/sell-players/", SellPlayersApi.as_view(), name="team-sell-players"),
]

urlpatterns += router.urls
