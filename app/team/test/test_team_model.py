"""
Test for Team model.
"""

from django.test import TestCase
from ..import models


class ModelTeamTest(TestCase):
    """Test team model."""
    def test_create_team(self):
        """Test creating a team is successful."""
        team = models.Team.objects.create(
            name='Team name',
        )
        self.assertEqual(str(team), team.name)
