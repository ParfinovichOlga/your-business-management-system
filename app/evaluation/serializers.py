"""
Serializer for Evaluation view.
"""

from rest_framework import serializers
from evaluation.models import Evaluation


class EvaluationSerializer(serializers.ModelSerializer):
    """Serializer for evaluations."""
    class Meta:
        model = Evaluation
        fields = '__all__'
        read_only_fields = ['id']
