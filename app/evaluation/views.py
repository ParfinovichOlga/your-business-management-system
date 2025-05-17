"""Views for Evaluation APIs."""

from rest_framework import viewsets, permissions
from evaluation.serializers import EvaluationSerializer
from evaluation.models import Evaluation
from rest_framework_simplejwt.authentication import JWTAuthentication
from core.permissions import IsManagerOrReadOnly
from django.db.models import Subquery, Avg
from task.models import Task


class EvaluationAPIView(viewsets.ModelViewSet):
    """View for managing evaluation API."""
    serializer_class = EvaluationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        IsManagerOrReadOnly
        ]
    queryset = Evaluation.objects.all()

    def get_queryset(self):
        if self.request.user.is_manager:
            return self.queryset.filter(user=self.request.user).order_by('-id')
        return self.queryset.filter(
            task_id__in=Subquery(
                Task.objects.filter(
                    assign_to=self.request.user, status='done'
                    ).values('pk'))
            ).select_related('task_id').order_by('-id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        if self.request.user.is_manager:
            return response
        response_data = {'result': response.data}
        response_data['avg_grade'] = queryset.aggregate(
            avg_grade=Avg('grade')).get('avg_grade')
        response.data = response_data
        return response

    def perform_create(self, serializer):
        """Create a new evaluation."""
        serializer.save(user=self.request.user)
