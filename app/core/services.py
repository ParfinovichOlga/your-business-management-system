from django.utils import timezone
from django.db.models.query import QuerySet

from team.models import Team
from user.models import User
from task.models import Task
from user.serializers import UserSerializer
from typing import Optional, Dict
from .forms import TeamForm, TaskForm


def select_all_teams() -> QuerySet:
    """Select and return all company teams."""
    teams = Team.objects.all().prefetch_related('members').order_by('name')
    return teams


def select_meetings_for_month(user: User) -> QuerySet:
    """Select and return user's meetings for current month."""
    month_meetings = user.meetings.filter(
            date__month=timezone.now().month, date__gte=timezone.now()
            ).all().order_by('date')
    return month_meetings


def select_meetings_for_today(user: User) -> QuerySet:
    """Select user's meetings for today."""
    today_meetings = user.meetings.filter(
            date__day=timezone.now().day,
            ).order_by('date')
    return today_meetings


def select_tasks_for_month(user: User) -> QuerySet:
    """Select and return user's tasks for month"""
    if user.is_manager:
        month_tasks = user.created_tasks.filter(
            deadline__month=timezone.now().month).order_by('deadline')
    else:
        month_tasks = user.tasks.filter(
            deadline__month=timezone.now().month).order_by('deadline')
    return month_tasks


def select_tasks_for_today(user: User) -> QuerySet:
    """Select and return user's tasks for today."""
    if user.is_manager:
        today_tasks = user.created_tasks.filter(
            deadline__day=timezone.now().day).order_by('deadline')
    else:
        today_tasks = user.tasks.filter(
            deadline__day=timezone.now().day).order_by('deadline')
    return today_tasks


def select_all_manager_tasks(user: User) -> Optional[QuerySet]:
    """Select and return all tasks created by manager, except rated."""
    if user.is_manager:
        tasks = user.created_tasks.all().select_related(
            'evaluation').filter(evaluation=None)
        return tasks
    return None


def sellect_all_available_employee_tasks(user: User) -> QuerySet:
    """Select all tasks that have been created by user's manager."""
    try:
        available_tasks = Task.objects.filter(
            user=user.team.manager, assign_to=None
            ).all().order_by('deadline')
    except Exception:
        available_tasks = Task.objects.all().order_by('deadline')
    return available_tasks


def select_all_emploee_tasks_todo(user: User) -> QuerySet:
    """Select all user's tasks todo."""
    return user.tasks.all().order_by('deadline')


def get_context_for_starting_page(user: User) -> dict:
    """Get and return context for starting page"""
    context = {}
    if user.is_authenticated:
        context['month_meetings'] = select_meetings_for_month(user)
        context['today_meetings'] = select_meetings_for_today(user)
        if user.is_superuser:
            context['team_form'] = TeamForm()
            context['teams'] = select_all_teams()
            return context
        context['month_tasks'] = select_tasks_for_month(user)
        context['today_tasks'] = select_tasks_for_today(user)
        if user.is_authenticated and user.is_manager:
            context['tasks'] = select_all_manager_tasks(user)
            context['task_form'] = TaskForm()
            return context
        context['tasks'] = sellect_all_available_employee_tasks(user)
        context['todo_tasks'] = select_all_emploee_tasks_todo(user)
        return context
    return context


def save_user(data: Dict):
    """Create and return user."""
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        return {'user': user}
    else:
        messages = []
        for k, v in serializer.errors.items():
            messages.append(f'{k}: {v[0].title()}')
        return {'messages': messages}


def update_profile(user: User, data: Dict):
    """Update user name or password."""
    if len(data['password']) < 5:
        return {'error': 'Ensure your password has at least 5 characters.'}
    if not data['name']:
        return {'error': 'Please fill out your name.'}

    user.name = data['name']
    user.set_password(data['password'])
    user.save()
    return {'user': user, 'message': 'You profile has apdated!'}


def save_team(data: Dict):
    """Save team to database."""
    members = data.pop('members', [])
    print(members)
    team = Team.objects.create(**data)
    appoint_manager(team, team.manager)
    team.members.set(members)


def appoint_manager(team: Team, manager: User):
    if manager:
        manager.is_manager = True
        manager.team = team
        manager.save()


def unpin_manager(manager: User):
    if manager:
        manager.is_manager = False
        manager.team = None
        manager.save()
