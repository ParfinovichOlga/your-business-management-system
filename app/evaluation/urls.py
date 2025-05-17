"""
URL mapping for the evaluation API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from evaluation.views import EvaluationAPIView

router = DefaultRouter()
router.register('evaluations', EvaluationAPIView)

app_name = 'evaluation'

urlpatterns = [
    path('', include(router.urls))
]
