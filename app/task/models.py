"""
Database Task model.
"""

from django.db import models
from django.conf import settings


class Task(models.Model):
    """Task object."""
    task_status = (
        ('opened', 'opened'), ('in_progress', 'in progress'), ('done', 'done')
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, related_name='created_tasks'
        )
    description = models.TextField()
    status = models.CharField(
        max_length=15, choices=task_status, default='opened'
        )
    deadline = models.DateField()
    assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
        )

    def __str__(self):
        return self.description


class Comment(models.Model):
    """Comment object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    date = models.DateField(auto_now=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text
