import django_filters

from .models import Player


class PlayerFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = ("id", "name")


class TeamFilter(django_filters.FilterSet):
    class Meta:
        model = Player
        fields = ("name",)
