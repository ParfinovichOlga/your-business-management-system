"""
Serializers for the task API View.
"""

from rest_framework import serializers
from task.models import Task, Comment


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the comment object."""
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['id']


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for the task object."""
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id']


class TaskDetailSerializer(TaskSerializer):
    """Serializer for task detail view."""
    comments = CommentSerializer(many=True, required=False)

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields
