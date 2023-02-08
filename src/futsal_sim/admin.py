from django.contrib import admin

from .models import MatchGoal, MatchResult, Player, Team, TeamLineup, TeamSheet

admin.site.register(Player)
admin.site.register(Team)
admin.site.register(TeamSheet)
admin.site.register(TeamLineup)
admin.site.register(MatchResult)
admin.site.register(MatchGoal)
