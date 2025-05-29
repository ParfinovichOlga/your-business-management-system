from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import TemplateView


from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Subquery, Avg
from django.http import HttpResponseRedirect
from django.urls import reverse
from .services import (
    appoint_manager, unpin_manager,
    get_context_for_starting_page, save_user,
    update_profile, save_team
)
from .forms import TeamForm, MeetingForm, TaskForm, CommentForm, EvaluationForm
from team.models import Team
from meeting.models import Meeting
from task.models import Task
from evaluation.models import Evaluation


def starting_page(request):
    """View for starting page."""
    context = get_context_for_starting_page(request.user)
    return render(request, 'index.html', context)


def sign_in(request):
    """View for login."""
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(
                request, 'Invalid email or password, please try again.'
                )
    return render(request, 'login.html')


def register(request):
    """View for creating a new user."""
    if request.method == 'POST':
        data = {
            'email': request.POST['email'],
            'password': request.POST['password'],
            'name': request.POST['name']
        }
        result = save_user(data)

        if result.get('user'):
            login(request, result['user'])
            return redirect('home')
        else:
            for message in result['messages']:
                messages.error(request, message)
    return render(request, 'register.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    return redirect('home')


@login_required
def update_user(request):
    """View for updating user's profile."""
    if request.method == 'POST':
        data = {
            'password': request.POST['password'],
            'name': request.POST['name']
        }
        result = update_profile(request.user, data)

        if result.get('user'):
            messages.info(request, result.get('message'))
            login(request, result.get('user'))
            return redirect('home')
        else:
            messages.error(request, result.get('error'))
    return render(request, 'update_user.html')


@login_required
def delete_profile(request):
    """Delete user profile."""
    profile = request.user
    profile.delete()
    return redirect('home')


@login_required
def create_team(request):
    if not request.user.is_superuser:
        return redirect('home')
    form = TeamForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            data = {
                'name': form.cleaned_data['name'],
                'manager': form.cleaned_data['manager'],
                'members': form.cleaned_data['members']
            }
            save_team(data)

        return redirect('home')
    messages.error(request, 'Team was not created. Please, try again')
    return redirect('home')


@login_required
def team_detail(request, id):
    if not request.user.is_superuser:
        return redirect('home')
    try:
        team = get_object_or_404(Team, id=int(id))
        inital = {
            'name': team.name,
            'manager': team.manager,
            'members': team.members.all()
            }
        form = TeamForm(initial=inital)
        if request.method == 'POST':
            form = TeamForm(request.POST)
            if form.is_valid():
                if team.manager != form.cleaned_data['manager']:
                    unpin_manager(team.manager)
                team.members.set([])
                team.name = form.cleaned_data['name']
                team.manager = form.cleaned_data['manager']
                team.members.set(form.cleaned_data['members'])
                team.save()
                appoint_manager(team, form.cleaned_data['manager'])
                return redirect('home')

        return render(
            request, 'team_detail.html', {'form': form, 'team': team}
            )
    except Exception:
        return render(
            request, 'team_detail.html', {'form': False, 'team': False})


@login_required
def delete_team(request, id):
    if not request.user.is_superuser:
        return redirect('home')
    team = get_object_or_404(Team, id=int(id))
    team.delete()
    return redirect('home')


class MeetingView(LoginRequiredMixin, View):
    def get(self, request):
        form = MeetingForm()
        context = {
            'form': form,
            'meetings': request.user.created_meetings.all().order_by('date')
        }
        return render(request, 'meeting.html', context)

    def post(self, request):
        form = MeetingForm(request.POST)
        if form.is_valid():
            try:
                meetings = request.user.meetings.all()
                overlay = next(
                    m for m in meetings if abs(
                        (
                            m.date - form.cleaned_data['date']
                        ).total_seconds()) < 3600
                        )

            except StopIteration:
                meeting = form.save(commit=False)
                meeting.user = request.user
                meeting.save()
                meeting.participants.set(form.cleaned_data['participants'])
                meeting.participants.add(request.user)
                return redirect('home')
            else:
                messages.error(
                request, f"You have a meeting  {overlay.title} at {overlay.date}"
                )

        return render(request, 'meeting.html', {'form': form})


@login_required
def delete_meeting(request, id):
    meeting_to_delete = get_object_or_404(Meeting, id=id)
    if request.user == meeting_to_delete.user:
        meeting_to_delete.delete()
        return redirect('set_up_meeting')


@login_required
def create_task(request):
    if request.method == 'POST' and request.user.is_manager:
        form = TaskForm(request.POST)
        if form.is_valid:
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('home')


@login_required
def task_detail(request, id):
    evaluation_form = EvaluationForm()
    comment_form = CommentForm()
    task = get_object_or_404(Task, id=int(id))
    if request.method == 'GET':
        return render(
            request, 'task_detail.html',
            {'task': task, 'comment_form': comment_form, ''
             'ev_form': evaluation_form})
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return HttpResponseRedirect(reverse("task_detail", args=[id]))
        return render(
            request, 'task_detail.html',
            {'task': task, 'comment_form': form, 'ev_form': evaluation_form})


@login_required
def update_task(request, id):
    if request.user.is_manager:
        task = get_object_or_404(Task, id=int(id))
        inital = {
                'user': task.user,
                'description': task.description,
                'status': task.status,
                'deadline': task.deadline,
                'assign_to': task.assign_to
                }
        form = TaskForm(initial=inital)
        if request.method == "GET":
            return render(
                request, 'update_task.html', {'form': form, 'task': task}
                )
        if request.method == 'POST':
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('home')
            return render(request, 'update_task.html', {'form': form})
    return redirect('home')


@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, id=id)
    if request.user.is_manager:
        task.delete()
    else:
        messages.error(
            request, 'You do not have permission to delete this task'
            )
        return HttpResponseRedirect(reverse("task_detail", args=[id]))
    return redirect('home')


@login_required
def evaluate_task(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if task.status != 'done':
            messages.error(
                request, 'Task should be completed before evaluating.'
                )
            return HttpResponseRedirect(reverse('task_detail', args=[id]))
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.user = request.user
            evaluation.task_id = task
            evaluation.save()
            return redirect('home')
        return HttpResponseRedirect(reverse('task_detail', args=[id]))


@login_required
def take_task(request, id):
    task = get_object_or_404(Task, id=id)
    task.assign_to = request.user
    task.status = 'in progress'
    task.save()
    return redirect('home')


@login_required
def mark_task_as_done(request, id):
    task = get_object_or_404(Task, id=id)
    if task.assign_to == request.user:
        task.status = 'done'
        task.save()
    return redirect('home')


class EvaluationView(LoginRequiredMixin, TemplateView):
    template_name = 'evaluations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluations'] = Evaluation.objects.all().filter(
            task_id__in=Subquery(
                Task.objects.filter(
                    assign_to=self.request.user, status='done'
                    ).values('pk'))
            ).select_related('task_id').order_by('-id')
        context['avg_evaluation'] = context['evaluations'].aggregate(
            avg_grade=Avg('grade')).get('avg_grade')
        return context
