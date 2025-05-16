"""
Django admin customation.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from user.models import User
from task.models import Task, Comment
from team.models import Team


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_staff',
                    'is_manager',
                    'is_superuser',
                    'is_active',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_staff',
                'is_manager',
                'is_superuser',
                'is_active',
            ),
        }),
    )


class TaskAdmin(admin.ModelAdmin):
    list_display = ('description',)
    list_filter = ('status', 'deadline')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')


admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment)
admin.site.register(Team, TeamAdmin)
