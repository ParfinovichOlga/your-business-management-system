"""
Serializers for the team API View.
"""

from rest_framework import serializers
from team.models import Team
from user.serializers import UserSerializer


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for list team object."""
    class Meta:
        model = Team
        fields = '__all__'
        read_only = ['id']


class TeamDetailSerializer(TeamSerializer):
    """Serializer for team object."""
    members = UserSerializer(many=True, required=False)

    class Meta(TeamSerializer.Meta):
        fields = TeamSerializer.Meta.fields
