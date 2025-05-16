"""
Views for team API.
"""

from rest_framework import viewsets, permissions

from rest_framework_simplejwt.authentication import JWTAuthentication

from team.serializers import TeamDetailSerializer, TeamSerializer
from team.models import Team

from core.permissions import IsAdminOrReadOnly


class TeamAPIView(viewsets.ModelViewSet):
    """View for managing team APIs."""
    serializer_class = TeamDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = Team.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.order_by('-id')
        else:
            return self.queryset.prefetch_related('members').order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return TeamSerializer
        return self.serializer_class
