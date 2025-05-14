"""Custom permissions for Task model."""
from rest_framework import permissions


class IsManagerOrReadOnly(permissions.BasePermission):
    """Allow changes for manager or read only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_manager)
