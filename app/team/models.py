"""
Database team model.
"""

from django.db import models


class Team(models.Model):
    """Team object."""
    name = models.CharField(max_length=25)
    manager = models.ForeignKey(
        'user.User', on_delete=models.SET_NULL,
        null=True, related_name='team_manager')

    def __str__(self):
        return self.name
