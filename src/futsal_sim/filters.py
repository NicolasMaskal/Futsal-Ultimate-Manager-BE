import django_filters

from .models import Player, Team, TeamSheet


class PlayerFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = ("name",)


class TeamFilter(django_filters.FilterSet):
    class Meta:
        model = Team
        fields = ("name",)


class TeamSheetFilter(django_filters.FilterSet):
    class Meta:
        model = TeamSheet
        fields = ("name",)
