from django.contrib import admin
from .models import Player, Team, TeamSheet, MatchResult


admin.site.register(Player)
admin.site.register(Team)
admin.site.register(TeamSheet)
admin.site.register(MatchResult)
