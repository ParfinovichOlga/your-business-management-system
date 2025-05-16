"""
URL mapping for the team API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from team.views import TeamAPIView

router = DefaultRouter()
router.register('teams', TeamAPIView)

app_name = 'team'

urlpatterns = [
    path('', include(router.urls))
]
