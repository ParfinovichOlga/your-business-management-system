"""
Views for the task API.
"""
from rest_framework import generics, permissions, mixins, viewsets

from task.serializers import TaskSerializer
from task.permissions import IsManagerOrReadOnly

from rest_framework_simplejwt.authentication import JWTAuthentication

from task.models import Task


class CreateTaskAPIView(generics.CreateAPIView):
    """Create new task."""
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsManagerOrReadOnly]


class ListTaskAPIView(generics.ListAPIView):
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all().order_by('-id')


class ManageTasksAPIView(mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    queryset = Task.objects.all()

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.order_by('-id')
        else:
            return self.queryset.prefetch_related('comments').order_by('-id')
