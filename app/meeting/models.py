"""
Database Meeting model.
"""

from django.db import models
from user.models import User


class Meeting(models.Model):
    """Meeting object."""
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    participants = models.ManyToManyField(
        User, related_name='meetings'
        )

    def __str__(self):
        return self.title
