"""
Database Evaluation model.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from task.models import Task


class Evaluation(models.Model):
    """Evaluation object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='evaluations',
        null=True
    )
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
        )
    task_id = models.OneToOneField(
        Task, on_delete=models.CASCADE,
        related_name='evaluation'
        )

    def __str__(self):
        return f'task {self.task_id} - {self.grade}'
