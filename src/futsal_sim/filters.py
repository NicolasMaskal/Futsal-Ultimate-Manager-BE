import django_filters

from .models import Player, Team, TeamSheet


class PlayerFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = ("name",)


class TeamFilter(django_filters.FilterSet):
    owner = django_filters.NumberFilter(field_name='owner__id')

    class Meta:
        model = Team
        fields = ["name", "owner"]


class TeamSheetFilter(django_filters.FilterSet):
    class Meta:
        model = TeamSheet
        fields = ("name",)
