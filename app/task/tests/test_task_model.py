"""
Test for Task model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from ..import models


class ModelTaskTest(TestCase):
    """Test task model."""
    def test_create_task(self):
        """Test creating a task is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        task = models.Task.objects.create(
            description='some description',
            status='in_progress',
            deadline='2025-06-01',
            assign_to=user
        )
        self.assertEqual(str(task), task.description)

    def test_create_comment(self):
        """Test creating a comment is successful."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        task = models.Task.objects.create(
            description='some description',
            deadline='2025-06-01'
        )
        comment = models.Comment.objects.create(
            user=user,
            task=task,
            text='An example comment'
        )
        self.assertEqual(str(comment), comment.text)
