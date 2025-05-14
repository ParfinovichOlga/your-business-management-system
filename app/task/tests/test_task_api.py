"""
Tests for task APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from task.models import Task
from task.serializers import TaskSerializer

from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime


TASK_URL = reverse('task:task-list')
CREATE_TASK_URL = reverse('task:create')


def detail_url(task_id):
    """Create and return a task detail URL."""
    return reverse('task:task-detail', args=[task_id])


def create_task(**params):
    """Create and return a sample task."""
    defaults = {
        'description': 'Sample description',
        'deadline': '2025-06-01'
    }
    defaults.update(params)
    task = Task.objects.create(**defaults)
    return task


def get_sample_task_payload():
    """Return sample payload for post task."""
    payload = {
            'description': 'Some description',
            'deadline': '2025-06-01'
        }
    return payload


class PublicTaskAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def auth_required(self):
        res1 = self.client.post(CREATE_TASK_URL, get_sample_task_payload())
        res2 = self.client.get(TASK_URL)
        self.assertEqual(res1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateManagerTaskAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        self.manager = get_user_model().objects.create(
            email='manager@example.com',
            password='testpass123',
            is_manager=True
        )
        self.client.force_authenticate(self.manager)

    def test_create_task_by_manager(self):
        """Test creating a task."""
        self.assertEqual(self.manager.is_manager, True)
        payload = get_sample_task_payload()
        res = self.client.post(CREATE_TASK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task = Task.objects.get(id=res.data['id'])

        self.assertEqual(getattr(task, 'description'), payload['description'])
        self.assertEqual(
            getattr(task, 'deadline'),
            datetime.strptime(payload['deadline'], '%Y-%m-%d').date()
            )


class PrivateUserTaskAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='testpass123'
        )

        self.client.force_authenticate(self.user)

    def test_create_task(self):
        """Test creating a task."""
        self.assertFalse(self.user.is_manager, True)

        res = self.client.post(CREATE_TASK_URL, get_sample_task_payload())
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_tasks(self):
        """Test retrieving a list of tasks."""
        create_task()
        create_task()

        res = self.client.get(TASK_URL)
        tasks = Task.objects.all().order_by('-id')
        serializer = TaskSerializer(tasks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_get_task_detail(self):
        """test get recipe detail."""
        task = create_task(assign_to=self.user)
        url = detail_url(task.id)
        res = self.client.get(url)
        serializer = TaskSerializer(task)
        self.assertEqual(res.data, serializer.data)

    def test_partial_update(self):
        """Test partial update for a task."""
        task = create_task()
        payload = {'status': 'done'}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, payload['status'])
