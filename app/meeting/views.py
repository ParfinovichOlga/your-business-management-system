"""
View for meeting APIs.
"""

from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from meeting.serializers import MeetingSerializer
from meeting.models import Meeting


class MeetingAPIView(viewsets.ModelViewSet):
    """View for managing meeting APIs."""
    serializer_class = MeetingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Meeting.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.request.user.meetings
        return self.queryset

    def perform_create(self, serializer):
        """Create a new meeting."""
        serializer.save(user=self.request.user)
