"""
"""
from django.urls import path, include
from task.views import CreateTaskAPIView, ManageTasksAPIView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tasks', ManageTasksAPIView)

app_name = 'task'

urlpatterns = [
    path('create/', CreateTaskAPIView.as_view(), name='create'),
    path('', include(router.urls)),
]
