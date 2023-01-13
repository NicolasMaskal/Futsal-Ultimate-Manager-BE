from rest_framework import serializers

from src.futsal_sim.models import Team


class TeamOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "wins",
            "draws",
            "loses",
            "coins",
        )
