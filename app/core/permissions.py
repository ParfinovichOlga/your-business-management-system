"""Custom permissions for models."""
from rest_framework import permissions


class IsManagerOrReadOnly(permissions.BasePermission):
    """Allow changes for manager or read only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_manager)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow changes for admin or read only"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow changes for owner or read only"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
