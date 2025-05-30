"""
Tests for task APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from task.models import Task, Comment
from task.serializers import TaskSerializer, TaskDetailSerializer

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

    def test_auth_required(self):
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
        serializer = TaskDetailSerializer(task)
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

    def test_full_update(self):
        """Test full update of recipe."""
        task = create_task(
                description='Sample task description.',
                deadline='2025-06-01',
                status='opened',
        )
        payload = {
            'description': 'New task description',
            'deadline': '2025-07-01',
            'status': 'in_progress',
        }
        url = detail_url(task.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        for k, v in payload.items():
            if k == 'deadline':
                self.assertEqual(getattr(task, k),
                                 datetime.strptime(v, '%Y-%m-%d').date())
            else:
                self.assertEqual(getattr(task, k), v)

    def test_delete_task(self):
        """Test deleting a recipe successful."""
        task = create_task()

        url = detail_url(task.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_comments_limited_to_task(self):
        """Test list of comments is limited to task."""
        task1 = create_task()
        task2 = create_task()
        comment1 = Comment.objects.create(
            user=self.user, task=task1, text='Comment for task1')
        Comment.objects.create(
            user=self.user, task=task2, text='Comment for task2')
        res = self.client.get(detail_url(task1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['comments']), 1)
        self.assertEqual(res.data['comments'][0]['id'], comment1.id)
        self.assertEqual(res.data['comments'][0]['text'], 'Comment for task1')
