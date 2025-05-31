"""
Tests for the meeting services.
"""

from django.test import TestCase
from unittest.mock import patch
from core.services import (
    select_meetings_for_month,
    have_meeting,
    save_meeting
)
from meeting.models import Meeting
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import pytz


class MeetingTests(TestCase):
    """Tests for meetings management."""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    @patch('core.services.timezone.now')
    def test_select_month_metings(self, mock_now):
        """Test retrieving user's month meetings."""
        mock_now.return_value = datetime(2025, 5, 31, 10, 30, tzinfo=pytz.UTC)
        meeting0 = Meeting.objects.create(
            title='Example title 0',
            date=datetime(2025, 5, 31, 9, 30, tzinfo=pytz.UTC)
        )
        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 6, 30, 14, 30, tzinfo=pytz.UTC)
        )
        meeting0.participants.add(self.user)
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.user)
        res = select_meetings_for_month(self.user)
        self.assertEqual(len(res), 1)
        self.assertIn(meeting1, res)
        self.assertNotIn(meeting2, res)

    def test_meetings_limited_to_user(self):
        """Test meetings limited to user."""
        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=timezone.now() + timedelta(seconds=1)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=timezone.now() + timedelta(seconds=1)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.other_user)

        res1 = select_meetings_for_month(self.user)
        self.assertEqual(len(res1), 1)
        res2 = select_meetings_for_month(self.other_user)
        self.assertEqual(len(res2), 1)

    @patch('core.services.timezone.now')
    def test_get_meetings_for_today(self, mock_now):
        """Test getting meetings for today."""
        mock_now.return_value = datetime(2025, 5, 31, 8, 30, tzinfo=pytz.UTC)

        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.user)

        res = select_meetings_for_month(self.user)
        self.assertEqual(len(res), 2)
        self.assertIn(meeting1, res)
        self.assertIn(meeting2, res)

    @patch('core.services.timezone.now')
    def test_get_meetings_for_today_limited_to_user(self, mock_now):
        """Test getting meetings for today limited to user."""
        mock_now.return_value = datetime(2025, 5, 31, 8, 30, tzinfo=pytz.UTC)

        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.other_user)

        res1 = select_meetings_for_month(self.user)
        self.assertEqual(len(res1), 1)
        res2 = select_meetings_for_month(self.other_user)
        self.assertEqual(len(res2), 1)

    def test_have_meetings(self):
        """Test user have no overlapping meetings"""
        date = datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        res = have_meeting(self.user, date)
        self.assertTrue(res['can_create'])
        meeting = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 17, 0, tzinfo=pytz.UTC)
        )
        meeting.participants.add(self.user)
        res1 = have_meeting(self.user, date)
        self.assertEqual(res1.get('can_create'), None)

    @patch('core.services.send_information_email')
    def test_create_meeting(self, mock_send):
        """Test create meeting."""
        mock_send.retutn_value = 'Messages were sent.'
        m = Meeting.objects.create(
            title='test',
            date=datetime(2025, 5, 31, 17, 0, tzinfo=pytz.UTC))
        save_meeting(m, self.user, [self.other_user])
        meetings = Meeting.objects.all()
        self.assertEqual(len(meetings), 1)
        self.assertEqual(meetings[0].user, self.user)
        self.assertEqual(len(meetings[0].participants.all()), 2)
