"""
Tests for evaluation APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Subquery

from task.models import Task

from evaluation.models import Evaluation
from evaluation.serializers import EvaluationSerializer

from rest_framework import status
from rest_framework.test import APIClient


EVALUATION_URL = reverse('evaluation:evaluation-list')


def detail_url(evaluation_id):
    """Create and return a task detail URL."""
    return reverse('evaluation:evaluation-detail', args=[evaluation_id])


def create_task(**params):
    """Create and return a sample task."""
    defaults = {
        'description': 'Sample description',
        'deadline': '2025-06-01'
    }
    defaults.update(params)
    task = Task.objects.create(**defaults)
    return task


class PublicTaskAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def auth_required(self):
        res = self.client.get(EVALUATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateManagerTaskAPITests(TestCase):
    """Test authenticated manager API requests."""
    def setUp(self):
        self.client = APIClient()
        self.manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='testpass123',
            is_manager=True
        )
        self.manager2 = get_user_model().objects.create_user(
            email='manager2@example.com',
            password='testpass123',
            is_manager=True
        )
        self.client.force_authenticate(self.manager)

    def test_create_evaluation_by_manager(self):
        """Test creating an evaluation."""
        self.assertEqual(self.manager.is_manager, True)
        task = create_task(status='done')
        payload = {'grade': 5, 'task_id': task.id}
        res = self.client.post(EVALUATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        evaluation = Evaluation.objects.get(id=res.data['id'])

        self.assertEqual(getattr(evaluation, 'grade'), payload['grade'])
        self.assertEqual(getattr(evaluation, 'task_id'), task)

    def test_retrieve_list_evaluations(self):
        """Test retrieving a list of all evaluations."""
        task1 = create_task(status='done')
        task2 = create_task(status='done')
        Evaluation.objects.create(user=self.manager, grade=5, task_id=task1)
        Evaluation.objects.create(user=self.manager, grade=5, task_id=task2)

        res = self.client.get(EVALUATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        evs = Evaluation.objects.all().order_by('-id')
        serializer = EvaluationSerializer(evs, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_evaluations_limited_by_manager(self):
        """Test evaluations limited by manager."""
        task1 = create_task(status='done')
        task2 = create_task(status='done')
        ev1 = Evaluation.objects.create(
            user=self.manager, grade=5, task_id=task1)
        Evaluation.objects.create(user=self.manager2, grade=1, task_id=task2)
        res = self.client.get(EVALUATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['grade'], ev1.grade)

    def test_delete_evaluation(self):
        """Test deleting an evaluation."""
        task = create_task(status='done')
        ev = Evaluation.objects.create(
            user=self.manager, grade=5, task_id=task)

        res = self.client.delete(detail_url(ev.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        com = Evaluation.objects.filter(id=ev.id)
        self.assertFalse(com.exists())


class EvaluetionPrivateAPITest(TestCase):
    """Test for authentecated requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test#example.com',
            password='test123'
        )
        self.client.force_authenticate(self.user)

    def test_get_list_evaluations(self):
        """Test retrieve list of evaluations."""
        task1 = Task.objects.create(
            description='1',
            deadline='2025-06-01',
            status='done',
            assign_to=self.user
        )
        task2 = Task.objects.create(
            description='2',
            deadline='2025-06-01',
            status='done',
            assign_to=self.user
        )

        ev1 = Evaluation.objects.create(grade=1, task_id=task1)
        ev2 = Evaluation.objects.create(grade=5, task_id=task2)
        res = self.client.get(EVALUATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        evs = Evaluation.objects.filter(task_id__in=Subquery(
                Task.objects.filter(
                    assign_to=self.user, status='done'
                    ).values('pk'))
                ).order_by('-id')
        serializer = EvaluationSerializer(evs, many=True)
        self.assertEqual(res.data['result'], serializer.data)
        self.assertEqual(res.data['avg_grade'], (ev1.grade + ev2.grade)/2)

    def test_evaluations_limited_to_user(self):
        """Test retrieve list of evaluations limited to user."""
        other_user = get_user_model().objects.create(
            email='e@ex.com',
            password='123456'
        )
        task1 = Task.objects.create(
            description='1',
            deadline='2025-06-01',
            status='done',
            assign_to=self.user
        )
        task2 = Task.objects.create(
            description='2',
            deadline='2025-06-01',
            status='done',
            assign_to=other_user
        )

        ev1 = Evaluation.objects.create(grade=1, task_id=task1)
        Evaluation.objects.create(grade=5, task_id=task2)
        res = self.client.get(EVALUATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        evs = Evaluation.objects.filter(task_id__in=Subquery(
                Task.objects.filter(
                    assign_to=self.user, status='done'
                    ).values('pk'))
                ).order_by('-id')
        serializer = EvaluationSerializer(evs, many=True)
        self.assertEqual(len(res.data['result']), 1)
        self.assertEqual(res.data['result'], serializer.data)
        self.assertEqual(res.data['avg_grade'], ev1.grade)

    def test_create_evaluation(self):
        """Test creating an evaluation."""
        task = create_task(status='done')
        payload = {'grade': 5, 'task_id': task.id}
        res = self.client.post(EVALUATION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
