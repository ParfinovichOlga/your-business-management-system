"""
Test for Meeting model.
"""

from django.test import TestCase
from meeting.models import Meeting
from datetime import datetime
import pytz


class ModelMeetingTest(TestCase):
    """Test meeting model."""
    def test_create_meeting(self):
        """Test creating a meeting is successful."""
        meeting = Meeting.objects.create(
            title='Example title',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        self.assertEqual(str(meeting), meeting.title)
