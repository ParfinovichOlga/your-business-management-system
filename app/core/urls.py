from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from .import views

urlpatterns = [
    path('', views.starting_page, name='home'),
    path('login/', views.sign_in, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(
        next_page=settings.LOGOUT_REDIRECT_URL
        ), name='logout'),
    path('profile/update/', views.update_user, name='update_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('team/create', views.create_team, name='create_team'),
    path('team/delete/<id>', views.delete_team, name='delete_team'),
    path('team/<id>', views.team_detail, name='team_detail'),
    path('take_task/<id>', views.take_task, name='take_task'),
    path('meeting/', views.MeetingView.as_view(), name='set_up_meeting'),
    path('meeting/cancel/<id>', views.delete_meeting, name='cancel_meeting'),
    path('task/create', views.create_task, name='create_task'),
    path('task/update/<id>', views.update_task, name='update_task'),
    path('task/delete/<id>', views.delete_task, name='delete_task'),
    path('task/evaluate/<id>', views.evaluate_task, name='evaluate_task'),
    path('task/done/<id>', views.mark_task_as_done, name='task_done'),
    path('task/<id>', views.task_detail, name='task_detail'),
    path('evaluations/', views.EvaluationView.as_view(), name='evaluation')

]
