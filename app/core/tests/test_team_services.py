"""
Tests for the team services.
"""

from django.test import TestCase
from unittest.mock import patch
from core.services import (
    select_all_teams,
    save_team, update_team,
)

from team.models import Team
from django.contrib.auth import get_user_model


class TeamsTests(TestCase):
    """Tests for team management."""
    def test_get_teams(self):
        """Test getting list of teams."""
        Team.objects.create(name='first')
        Team.objects.create(name='second')
        res = select_all_teams()
        self.assertEqual(len(res), 2)

    def test_no_teams(self):
        """Test get empty list of teams"""
        res = select_all_teams()
        self.assertEqual(len(res), 0)

    def test_create_team(self):
        """Test creating team."""
        user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        user3 = get_user_model().objects.create_user(
            email='user3@example.com',
            password='testpass123'
        )
        data = {
            'name': 'Test team',
            'manager': user1,
            'members': [user2, user3]
        }
        save_team(data)
        team = Team.objects.get(name=data['name'])
        self.assertEqual(team.name, data['name'])
        self.assertEqual(user1.team, team)
        self.assertEqual(user2.team, team)
        self.assertEqual(user2.team, team)
        self.assertTrue(user1.is_manager)
        self.assertEqual(len(team.members.all()), 3)

    def test_creating_team_without_members(self):
        data = {
            'name': 'Test team',
        }
        save_team(data)
        self.assertTrue(
            Team.objects.filter(name=data['name']).exists())

    def test_update_team(self):
        """Test updating team."""
        team = Team.objects.create(name='Test team')
        user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        data = {
            'name': 'New',
            'manager': user1,
            'members': [user2]
        }
        update_team(team, data)
        self.assertEqual(team.name, data['name'])
        self.assertEqual(team.manager, data['manager'])
        self.assertEqual(len(team.members.all()), 2)

    def test_update_team_manager(self):
        """Test updating team manager."""
        user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
            is_manager=True
        )
        team = Team.objects.create(
            name='Test team',
            manager=user1
        )
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        data = {
            'name': 'Test team',
            'manager': user2,
            'members': [user1]
        }
        update_team(team, data)
        self.assertEqual(team.manager, user2)
        self.assertTrue(user2.is_manager)
        self.assertFalse(user1.is_manager)
        self.assertEqual(len(team.members.all()), 2)

    def test_set_team_manager_to_none(self):
        """Test updating team."""
        user1 = get_user_model().objects.create_user(
            email='user1@example.com',
            password='testpass123',
            is_manager=True
        )
        user2 = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        user3 = get_user_model().objects.create_user(
            email='user3@example.com',
            password='testpass123'
        )
        team = Team.objects.create(
            name='Test team',
            manager=user1
        )
        team.members.set([user2, user3])
        data = {
            'name': 'Test team',
            'manager': None,
            'members': [user2]
        }
        update_team(team, data)
        self.assertEqual(len(team.members.all()), 1)
        self.assertEqual(team.members.all()[0], user2)
        self.assertEqual(team.manager, None)
