"""
Tests for meeting APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from meeting.models import Meeting
from meeting.serializers import MeetingSerializer

from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime
import pytz


MEETING_URL = reverse('meeting:meeting-list')


def detail_url(meeting_id):
    """Create and return a meeting detail URL."""
    return reverse('meeting:meeting-detail', args=[meeting_id])


class PublicTaskAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MEETING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMeetingAPITests(TestCase):
    """Test authenticated  API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_list_meetings(self):
        """Test retrieving a list of all evaluations."""
        meet1 = Meeting.objects.create(
            title='First', date=datetime(
                2025, 5, 31, 14, 30, tzinfo=pytz.UTC))
        meet2 = Meeting.objects.create(
            title='Second', date=datetime(
                2025, 5, 31, 14, 30, tzinfo=pytz.UTC))
        Meeting.objects.create(title='Third', date=datetime(
            2025, 5, 31, 14, 30, tzinfo=pytz.UTC))

        meet1.participants.add(self.user)
        meet2.participants.add(self.user)

        res = self.client.get(MEETING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        serializer = MeetingSerializer(self.user.meetings, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_empty_meeting_list(self):
        """Test retrieving empty meeting list."""
        res = self.client.get(MEETING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, [])

    def test_get_meeting_details(self):
        """Test getting meeting details."""
        meet = Meeting.objects.create(
            title='First', date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC))
        res = self.client.get(detail_url(meet.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'First')
        self.assertEqual(res.data['date'], '2025-05-31T14:30:00Z')
        self.assertEqual(res.data['participants'], [])

    def test_full_meeting_update(self):
        """Test full meeting update."""
        meet = Meeting.objects.create(
            title='First',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC),
        )
        payload = {
            'title': 'Second',
            'date': '2025-05-31T15:30:00Z'
        }
        res = self.client.put(detail_url(meet.id), payload)
        meet.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Second')

    def test_create_meeting(self):
        """Test creating a new meeting."""
        payload = {
            'title': 'Meeting',
            'date': '2025-05-31T15:30:00Z'
        }
        res = self.client.post(MEETING_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], payload['title'])
