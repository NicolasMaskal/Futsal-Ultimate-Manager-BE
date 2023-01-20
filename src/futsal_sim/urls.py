from django.urls import path
from rest_framework_nested import routers

from src.futsal_sim.apis.matches_api import MatchApi
from src.futsal_sim.apis.packs_api import TeamBuyPackApi
from src.futsal_sim.apis.players_api import PlayerListApi
from src.futsal_sim.apis.teams_api import SellPlayersApi, TeamApi
from src.futsal_sim.apis.teamsheet_api import TeamSheetCRUDApi

urlpatterns = [
    path("teams/<int:team_id>/players/", PlayerListApi.as_view(), name="team-players"),
    path("teams/<int:team_id>/buy-pack/", TeamBuyPackApi.as_view(), name="team-buy-pack"),
    path("teams/<int:team_id>/sell-players/", SellPlayersApi.as_view(), name="team-sell-players"),
]

router = routers.SimpleRouter()
router.register(r"teams", TeamApi, "teams")
teams_router = routers.NestedSimpleRouter(router, r"teams", lookup="team")
teams_router.register(r"team-sheets", TeamSheetCRUDApi, basename="team-sheets")
teams_router.register(r"match-results", MatchApi, basename="match-results")

urlpatterns += router.urls
urlpatterns += teams_router.urls
