"""
Tests for the services funcrions.
"""

from django.test import TestCase
from unittest.mock import patch
from core.services import (
    select_all_teams, select_meetings_for_month,
    select_tasks_for_month, select_tasks_for_today,
    select_all_manager_tasks, sellect_all_available_employee_tasks,
    select_all_emploee_tasks_todo, get_context_for_starting_page,
    save_user, update_profile, save_team, update_team, have_meeting,
    save_meeting, select_user_evaluations
)
from user.models import User
from meeting.models import Meeting
from task.models import Task
from team.models import Team
from evaluation.models import Evaluation
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from datetime import datetime, timedelta
import pytz


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


class MeetingTests(TestCase):
    """Tests for meetings management."""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    @patch('core.services.timezone.now')
    def test_select_month_metings(self, mock_now):
        """Test retrieving user's month meetings."""
        mock_now.return_value = datetime(2025, 5, 31, 10, 30, tzinfo=pytz.UTC)
        meeting0 = Meeting.objects.create(
            title='Example title 0',
            date=datetime(2025, 5, 31, 9, 30, tzinfo=pytz.UTC)
        )
        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 6, 30, 14, 30, tzinfo=pytz.UTC)
        )
        meeting0.participants.add(self.user)
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.user)
        res = select_meetings_for_month(self.user)
        self.assertEqual(len(res), 1)
        self.assertIn(meeting1, res)
        self.assertNotIn(meeting2, res)

    def test_meetings_limited_to_user(self):
        """Test meetings limited to user."""
        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=timezone.now() + timedelta(seconds=1)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=timezone.now() + timedelta(seconds=1)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.other_user)

        res1 = select_meetings_for_month(self.user)
        self.assertEqual(len(res1), 1)
        res2 = select_meetings_for_month(self.other_user)
        self.assertEqual(len(res2), 1)

    @patch('core.services.timezone.now')
    def test_get_meetings_for_today(self, mock_now):
        """Test getting meetings for today."""
        mock_now.return_value = datetime(2025, 5, 31, 8, 30, tzinfo=pytz.UTC)

        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.user)

        res = select_meetings_for_month(self.user)
        self.assertEqual(len(res), 2)
        self.assertIn(meeting1, res)
        self.assertIn(meeting2, res)

    @patch('core.services.timezone.now')
    def test_get_meetings_for_today_limited_to_user(self, mock_now):
        """Test getting meetings for today limited to user."""
        mock_now.return_value = datetime(2025, 5, 31, 8, 30, tzinfo=pytz.UTC)

        meeting1 = Meeting.objects.create(
            title='Example title 1',
            date=datetime(2025, 5, 31, 14, 30, tzinfo=pytz.UTC)
        )
        meeting2 = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        )
        meeting1.participants.add(self.user)
        meeting2.participants.add(self.other_user)

        res1 = select_meetings_for_month(self.user)
        self.assertEqual(len(res1), 1)
        res2 = select_meetings_for_month(self.other_user)
        self.assertEqual(len(res2), 1)

    def test_have_meetings(self):
        """Test user have no overlapping meetings"""
        date = datetime(2025, 5, 31, 16, 30, tzinfo=pytz.UTC)
        res = have_meeting(self.user, date)
        self.assertTrue(res['can_create'])
        meeting = Meeting.objects.create(
            title='Example title 2',
            date=datetime(2025, 5, 31, 17, 0, tzinfo=pytz.UTC)
        )
        meeting.participants.add(self.user)
        res1 = have_meeting(self.user, date)
        self.assertEqual(res1.get('can_create'), None)

    def test_create_meeting(self):
        """Test create meeting."""
        m = Meeting.objects.create(
            title='test',
            date=datetime(2025, 5, 31, 17, 0, tzinfo=pytz.UTC))
        save_meeting(m, self.user, [self.other_user])
        meetings = Meeting.objects.all()
        self.assertEqual(len(meetings), 1)
        self.assertEqual(meetings[0].user, self.user)
        self.assertEqual(len(meetings[0].participants.all()), 2)


class TaskTests(TestCase):
    """Tests for meetings management."""
    def setUp(self):
        self.manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='testpass123',
            is_manager=True
        )
        self.team = Team.objects.create(
            name='Test team', manager=self.manager)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            team=self.team
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    @patch('core.services.timezone.now')
    def test_select_tasks_for_month(self, mock_now):
        """Test retrieving tasks that have deadline in current month."""
        mock_now.return_value = datetime(2025, 5, 1, 8, 30, tzinfo=pytz.UTC)
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 31, tzinfo=pytz.UTC),
            assign_to=self.user
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 30, tzinfo=pytz.UTC)
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 6, 30, tzinfo=pytz.UTC)
        )
        res1 = select_tasks_for_month(self.user)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].assign_to, self.user)
        res2 = select_tasks_for_month(self.manager)
        self.assertEqual(len(res2), 2)
        self.assertEqual(
            res2[0].deadline, datetime(2025, 5, 30, tzinfo=pytz.UTC).date())
        self.assertEqual(
            res2[1].deadline, datetime(2025, 5, 31, tzinfo=pytz.UTC).date())

    @patch('core.services.timezone.now')
    def test_select_tasks_for_today(self, mock_now):
        """Test retrieving tasks that have deadline today."""
        mock_now.return_value = datetime(2025, 5, 1, 8, 30, tzinfo=pytz.UTC)
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.user
        )
        Task.objects.create(
            user=self.manager,
            description='some description',
            status='in_progress',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
        )

        res1 = select_tasks_for_today(self.user)
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0].assign_to, self.user)
        res2 = select_tasks_for_month(self.manager)
        self.assertEqual(len(res2), 2)

    def test_select_all_manager_tasks(self):
        """Test retrieving all manager created tasks."""
        task = Task.objects.create(
            user=self.manager,
            description='some description',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        Task.objects.create(
            user=self.manager,
            description='some description',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        Evaluation.objects.create(
            user=self.manager,
            grade=5,
            task_id=task
            )
        res = select_all_manager_tasks(self.manager)
        self.assertEqual(len(res), 1)
        self.assertNotIn(task, res)

    def test_sellect_all_available_employee_tasks(self):
        """Test retrieving all availabel tasks for user."""
        Task.objects.create(
            user=self.manager,
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.other_user
            )
        Task.objects.create(
            user=self.manager,
            description='Task that I can get.',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC)
            )
        res = sellect_all_available_employee_tasks(self.user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].description, 'Task that I can get.')

    def test_select_all_emploee_tasks_todo(self):
        """Test retrieving all user's todo tasks."""
        Task.objects.create(
            user=self.manager,
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.other_user
            )
        Task.objects.create(
            user=self.manager,
            description='My task.',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            assign_to=self.user
            )
        res = select_all_emploee_tasks_todo(self.user)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].description, 'My task.')


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


class EvaluationTests(TestCase):
    """Tests for evaluation."""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.other_user = get_user_model().objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

    def test_select_user_evaluations(self):
        """Test select user evaluations."""
        task1 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.user
            )
        task2 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.user
            )
        Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='in_progress',
            assign_to=self.user
            )
        task3 = Task.objects.create(
            description='Task for other user',
            deadline=datetime(2025, 5, 1, tzinfo=pytz.UTC),
            status='done',
            assign_to=self.other_user
            )
        Evaluation.objects.create(grade=1, task_id=task1)
        Evaluation.objects.create(grade=5, task_id=task2)
        Evaluation.objects.create(grade=4, task_id=task3)
        res = select_user_evaluations(self.user)
        self.assertEqual(len(res['evaluations']), 2)
        self.assertIn(task1.evaluation, res['evaluations'])
        self.assertIn(task2.evaluation, res['evaluations'])
        self.assertEqual(res['avg_evaluation'], 3.0)
