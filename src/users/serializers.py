from rest_framework import serializers

from src.futsal_sim.serializers import TeamOutputSerializer
from src.users.models import User


class UserOutputSerializer(serializers.ModelSerializer):
    active_team = TeamOutputSerializer()

    class Meta:
        model = User
        fields = ("id", "email", "is_admin", "active_team", "email_verified")
