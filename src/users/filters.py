import django_filters

from src.users.models import User


class BaseUserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ("id", "email", "is_admin")
