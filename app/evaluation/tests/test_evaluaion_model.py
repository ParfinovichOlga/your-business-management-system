"""
Test for Evaluation model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from task.models import Task
from evaluation.models import Evaluation


class ModelEvaluationTest(TestCase):
    """Test task model."""
    def test_create_evaluation(self):
        """Test creating an evaluation is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        task = Task.objects.create(
            description='some description',
            deadline='2025-06-01',
            status='done'
        )
        evaluation = Evaluation.objects.create(
            user=user,
            grade=5,
            task_id=task
        )
        self.assertEqual(
            str(evaluation), f'task {task.description} - {evaluation.grade}'
            )
