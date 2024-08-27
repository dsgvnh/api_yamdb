from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework import permissions


class IsAdmin(BasePermission):
    """
    Разрешает доступ только для суперпользователя или админа.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )


class IsReadOnly(BasePermission):
    """
    Доступ разрешен для безопасных методов (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class AdminModeratorAuthor(permissions.BasePermission):
    """
    Разрешает редактировать и удалять контент только автору,
     модератору или администратору.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
        )
