"""
Database Meeting model.
"""

from django.db import models
from django.conf import settings
from user.models import User


class Meeting(models.Model):
    """Meeting object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, related_name='created_meetings'
        )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    participants = models.ManyToManyField(
        User, related_name='meetings'
        )

    def __str__(self):
        return self.title
