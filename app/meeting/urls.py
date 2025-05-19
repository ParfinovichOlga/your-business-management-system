"""
URL mapping for meeting API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from meeting.views import MeetingAPIView


router = DefaultRouter()
router.register('meetings', MeetingAPIView)

app_name = 'meeting'

urlpatterns = [
    path('', include(router.urls))
]
