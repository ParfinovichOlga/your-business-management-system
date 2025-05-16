"""
Tests for the team API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from team.models import Team
from team.serializers import TeamSerializer, TeamDetailSerializer


TEAM_URL = reverse('team:team-list')


def detail_url(team_id):
    """Create and return comment detail url."""
    url = reverse('team:team-detail', args=[team_id])
    return url


class PublicCommentsAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving list of comments"""
        res = self.client.get(TEAM_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentsUserAPITests(TestCase):
    """Test authentecated user API requests."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email='testuser@example.com',
            password='test123'
        )
        self.client.force_authenticate(self.user)

    def test_create_team(self):
        """Test create a team by user."""
        payload = {'name': 'test team'}
        res = self.client.post(TEAM_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_teams(self):
        """Test getting teams by user is successed."""
        manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='test123',
            is_manager=True
        )
        Team.objects.create(name='first', manager=manager)
        Team.objects.create(name='second')
        res = self.client.get(TEAM_URL)
        teams = Team.objects.all().order_by('-id')
        serializer = TeamSerializer(teams, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)


class PrivateCommentsAdminUserAPITests(TestCase):
    """Test authentecated user API requests."""
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='12345'
        )
        self.client.force_authenticate(self.admin)

    def test_create_team(self):
        """Test create a team by admin."""
        payload = {'name': 'test team'}
        res = self.client.post(TEAM_URL, payload)
        team = Team.objects.all().get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], team.name)

    def test_user_limited_to_team(self):
        """Test users limited to team."""
        team1 = Team.objects.create(name='First')
        team2 = Team.objects.create(name='Second')
        get_user_model().objects.create_user(
            email='manager@example.com',
            password='test123',
            is_manager=True,
            team=team1
        )
        get_user_model().objects.create_user(
            email='user1@example.com',
            password='test123',
            team=team1
        )
        get_user_model().objects.create_user(
            email='user2@example.com',
            password='test123',
            team=team2
        )
        res = self.client.get(detail_url(team1.id))
        team = Team.objects.get(id=team1.id)
        serialiser = TeamDetailSerializer(team)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['members']), 2)
        self.assertEqual(res.data, serialiser.data)

    def test_partial_update_team(self):
        """Test partial update team."""
        team = Team.objects.create(name='test')
        manager = get_user_model().objects.create_user(
            email='manager@example.com',
            password='test123',
        )

        payload = {'manager': manager.id}
        res = self.client.patch(detail_url(team.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.manager, manager)
        self.assertEqual(team.name, 'test')
