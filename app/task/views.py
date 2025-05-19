"""
Views for the task API.
"""
from rest_framework import generics, permissions, mixins, viewsets

from task.serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    CommentSerializer
)
from core.permissions import IsManagerOrReadOnly, IsOwnerOrReadOnly

from rest_framework_simplejwt.authentication import JWTAuthentication

from task.models import Task, Comment


class CreateTaskAPIView(generics.CreateAPIView):
    """Create new task."""
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsManagerOrReadOnly]

    def perform_create(self, serializer):
        """Create a new task."""
        serializer.save(user=self.request.user)


class ManageTasksAPIView(mixins.DestroyModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """View for managing task APIs."""
    serializer_class = TaskDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.order_by('-id')
        else:
            return self.queryset.prefetch_related('comments').order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return TaskSerializer
        return self.serializer_class


class CommentAPIView(viewsets.ModelViewSet):
    """View for managing comments APIs."""
    serializer_class = CommentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Comment.objects.all().order_by('-id')
