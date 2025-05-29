from django import forms
from user.models import User
from meeting.models import Meeting
from task.models import Task, Comment
from evaluation.models import Evaluation
from formset.widgets import DateTimeTextbox, DateTextbox


class TeamForm(forms.Form):
    name = forms.CharField(label='title', max_length=100)
    manager = forms.ModelChoiceField(
        label='manager', queryset=User.objects.all()
        )
    members = forms.ModelMultipleChoiceField(
        label='memebers', queryset=User.objects.all()
        )


class MeetingForm(forms.ModelForm):

    class Meta:
        model = Meeting
        exclude = ['user', ]

        widgets = {
            'date': DateTimeTextbox,
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15})

        }


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        exclude = ['user', ]

        widgets = {
            'deadline': DateTextbox,
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 15})

        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ['user', 'task']

        widgets = {
            'test': forms.Textarea(attrs={'rows': 4, 'cols': 4})
        }


class EvaluationForm(forms.ModelForm):

    class Meta:
        model = Evaluation
        exclude = ['user', 'task_id']
