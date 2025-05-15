"""
"""
from django.urls import path, include
from task.views import CreateTaskAPIView, ManageTasksAPIView, CommentAPIView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('tasks', ManageTasksAPIView)
router.register('comments', CommentAPIView)

app_name = 'task'

urlpatterns = [
    path('create/', CreateTaskAPIView.as_view(), name='create'),
    path('', include(router.urls)),
]
