"""
Tests for the comments API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from task.models import Comment
from task.serializers import CommentSerializer
from .test_task_api import create_task

COMMENTS_URL = reverse('task:comment-list')


def detail_url(comment_id):
    """Create and return comment detail url."""
    url = reverse('task:comment-detail', args=[comment_id])
    return url


def create_comment(user, task, **params):
    """Create and return a comment sample."""
    defaults = {
        'text': 'It is a sample comment.',
    }
    defaults.update(params)
    comment = Comment.objects.create(user=user, task=task, **defaults)
    return comment


class PublicCommentsAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving list of comments"""
        res = self.client.get(COMMENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentsAPITests(TestCase):
    """Tests authenticated API requests."""
    def setUp(self):
        self.user = get_user_model().objects.create(
                email='test@example.com',
                password='test12345')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_list_comments(self):
        """Test retrieving list of comments."""
        task = create_task()
        create_comment(self.user, task)
        create_comment(self.user, task)

        res = self.client.get(COMMENTS_URL)

        comments = Comment.objects.all().order_by('-id')
        serializer = CommentSerializer(comments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_comment(self):
        """Test updating a task."""
        task = create_task()
        comment = Comment.objects.create(
            user=self.user, task=task, text='first comment'
            )
        payload = {'text': 'second comment'}
        url = detail_url(comment_id=comment.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, payload['text'])

    def test_delete_comment(self):
        """Test deleting an ingredient."""
        task = create_task()
        comment = Comment.objects.create(
            user=self.user, task=task, text='first comment')
        url = detail_url(comment.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        com = Comment.objects.filter(id=comment.id)
        self.assertFalse(com.exists())

    def test_delete_update_other_user_comment(self):
        """Test deleting/updating other user comment."""
        task = create_task()
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='test123'
        )
        comment = Comment.objects.create(
            user=other_user, task=task, text='first comment')
        res1 = self.client.delete(detail_url(comment.id))
        self.assertEqual(res1.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=comment.id).exists())
        res2 = self.client.patch(detail_url(comment.id), {'text': ''})
        self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)
