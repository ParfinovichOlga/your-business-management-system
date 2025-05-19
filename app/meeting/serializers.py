"""
Serializer for the Metting API View.
"""

from rest_framework import serializers
from meeting.models import Meeting
from user.serializers import UserSerializer


class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for the meeting object."""
    participants = UserSerializer(many=True, required=False)

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'date', 'description',
            'participants',
            ]
        read_only_fields = ['id']
