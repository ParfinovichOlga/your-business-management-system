"""
Tests for the task and evaluation services.
"""

from django.test import TestCase
from unittest.mock import patch
from core.services import (
    select_tasks_for_month, select_tasks_for_today,
    select_all_manager_tasks, sellect_all_available_employee_tasks,
    select_all_emploee_tasks_todo, select_user_evaluations
)
from task.models import Task
from team.models import Team
from evaluation.models import Evaluation
from django.contrib.auth import get_user_model
from datetime import datetime
import pytz


class TaskTests(TestCase):
    """Tests for meetings management."""
    def setUp(self):
        self.manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='testpass123',
            is_manager=True
        )
        self.team = Team.objects.create(
            name='Test team', manager=self.manager)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            team=self.team
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    @patch('core.services.timezone.now')
    def test_select_tasks_for_month(self, mock_now):
        """Test retrieving tasks that have deadline in current month."""
        mock_now.return_value = datetime(2025, 5, 1, 8, 30, tzinfo=pytz.UTC)
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 31, tzinfo=pytz.UTC),
            assign_to=self.user
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 30, tzinfo=pytz.UTC)
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 6, 30, tzinfo=pytz.UTC)
        )
        res1 = select_tasks_for_month(self.user)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].assign_to, self.user)
        res2 = select_tasks_for_month(self.manager)
        self.assertEqual(len(res2), 2)
        self.assertEqual(
            res2[0].deadline, datetime(2025, 5, 30, tzinfo=pytz.UTC).date())
        self.assertEqual(
            res2[1].deadline, datetime(2025, 5, 31, tzinfo=pytz.UTC).date())

    @patch('core.services.timezone.now')
    def test_select_tasks_for_today(self, mock_now):
        """Test retrieving tasks that have deadline today."""
        mock_now.return_value = datetime(2025, 5, 1, 8, 30, tzinfo=pytz.UTC)
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.user
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
        )

        res1 = select_tasks_for_today(self.user)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].assign_to, self.user)
        res2 = select_tasks_for_month(self.manager)
        self.assertEqual(len(res2), 2)

    def test_select_all_manager_tasks(self):
        """Test retrieving all manager created tasks."""
        task = Task.objects.create(
            user=self.manager,
            description='some description',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        Task.objects.create(
            user=self.manager,
            description='some description',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        Evaluation.objects.create(
            user=self.manager,
            grade=5,
            task_id=task
            )
        res = select_all_manager_tasks(self.manager)
        self.assertEqual(len(res), 1)
        self.assertNotIn(task, res)

    def test_sellect_all_available_employee_tasks(self):
        """Test retrieving all availabel tasks for user."""
        Task.objects.create(
            user=self.manager,
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.other_user
            )
        Task.objects.create(
            user=self.manager,
            description='Task that I can get.',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        res = sellect_all_available_employee_tasks(self.user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].description, 'Task that I can get.')

    def test_select_all_emploee_tasks_todo(self):
        """Test retrieving all user's todo tasks."""
        Task.objects.create(
            user=self.manager,
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.other_user
            )
        Task.objects.create(
            user=self.manager,
            description='My task.',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.user
            )
        res = select_all_emploee_tasks_todo(self.user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].description, 'My task.')


class EvaluationTests(TestCase):
    """Tests for evaluation."""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    def test_select_user_evaluations(self):
        """Test select user evaluations."""
        task1 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.user
            )
        task2 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.user
            )
        Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='in_progress',
            assign_to=self.user
            )
        task3 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.other_user
            )
        Evaluation.objects.create(grade=1, task_id=task1)
        Evaluation.objects.create(grade=5, task_id=task2)
        Evaluation.objects.create(grade=4, task_id=task3)
        res = select_user_evaluations(self.user)
        self.assertEqual(len(res['evaluations']), 2)
        self.assertIn(task1.evaluation, res['evaluations'])
        self.assertIn(task2.evaluation, res['evaluations'])
        self.assertEqual(res['avg_evaluation'], 3.0)
