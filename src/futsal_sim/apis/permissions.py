from rest_framework.permissions import BasePermission


class TeamPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user and request.user.is_superuser:
            return True
        return obj.owner == request.user


class OwnedByTeamPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user and request.user.is_superuser:
            return True
        return obj.team.owner == request.user
