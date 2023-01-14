from django.contrib import admin

from .models import MatchResult, Player, Team, TeamSheet

admin.site.register(Player)
admin.site.register(Team)
admin.site.register(TeamSheet)
admin.site.register(MatchResult)
