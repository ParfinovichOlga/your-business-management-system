"""
Tests for the user services.
"""

from django.test import TestCase
from unittest.mock import patch
from core.services import (
    get_context_for_starting_page,
    save_user, update_profile
)
from user.models import User
from django.contrib.auth import get_user_model, authenticate


class StartingPageContextTests(TestCase):
    """Tests for getting starting page context."""
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='testpass123',
            is_manager=True
        )

        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

    def test_get_context_for_starting_page(self):
        """Test getting starting page context."""
        admin_context = [
            'month_meetings',
            'today_meetings',
            'team_form',
            'teams'
        ]
        manager_context = [
            'month_meetings',
            'today_meetings',
            'month_tasks',
            'today_tasks',
            'tasks',
            'task_form'
        ]
        user_context = [
            'month_meetings',
            'today_meetings',
            'month_tasks',
            'today_tasks',
            'tasks',
            'todo_tasks'
        ]
        res_admin = get_context_for_starting_page(self.admin)
        self.assertEqual(len(res_admin), len(admin_context))
        for k in admin_context:
            self.assertIn(k, res_admin)

        res_manager = get_context_for_starting_page(self.manager)
        self.assertEqual(len(res_manager), len(manager_context))
        for k in manager_context:
            self.assertIn(k, res_manager)

        res_user = get_context_for_starting_page(self.user)
        self.assertEqual(len(res_user), len(user_context))
        for k in user_context:
            self.assertIn(k, res_user)


class UserTests(TestCase):
    """Tests for user managent."""
    def test_create_user(self):
        """Test successful user creation."""
        data = {
           'email': 'test@example.com',
           'password':  'test1',
           'name': 'test'
        }
        save_user(data)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_user_already_exists(self):
        """Test creating user who already exists."""
        data = {
            'email': 'user@example.com',
            'password': 'testpass123',
            'name': 'test'
        }
        get_user_model().objects.create_user(**data)
        res = save_user(data)

        self.assertEqual(
            res['messages'][0], 'email: User With This Email Already Exists.'
            )

    def test_invalid_password(self):
        """Test creating user with uinvalid password."""
        data = {
            'email': 'user@example.com',
            'password': '123',
            'name': 'test'
        }
        res = save_user(data)

        self.assertEqual(
            res.get('messages')[0],
            'password: Ensure This Field Has At Least 5 Characters.'
            )
        self.assertFalse(User.objects.filter(email=data['email']).exists())

    def test_update_profile(self):
        """Test updating profile."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='test'
        )
        data = {
            'name': 'New name',
            'password': 'newpassword'
        }
        res = update_profile(user, data)
        self.assertEqual(res['user'].name, data['name'])
        self.assertTrue(
            authenticate(email=user.email, password=data['password'])
            )

    def test_update_profile_invalid_data(self):
        """Test updating profile with invalid data."""
        user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='test'
        )
        data = {
            'name': '',
            'password': 'newpassword'
        }
        res = update_profile(user, data)
        self.assertNotIn('user', res)
        self.assertFalse(
            authenticate(email=user.email, password=data['password'])
            )

        data = {
            'name': 'test',
            'password': '123'
        }
        res = update_profile(user, data)
        self.assertNotIn('user', res)
        self.assertFalse(
            authenticate(email=user.email, password=data['password'])
            )
