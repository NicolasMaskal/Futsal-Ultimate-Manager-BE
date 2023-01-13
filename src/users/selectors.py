from django.db.models.query import QuerySet

from src.users.filters import BaseUserFilter
from src.users.models import User


def user_list(*, filters=None) -> QuerySet[User]:
    filters = filters or {}

    qs = User.objects.all()

    return BaseUserFilter(filters, qs).qs
