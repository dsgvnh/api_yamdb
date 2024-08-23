from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework import permissions


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return (
                request.user.is_superuser
                or request.user.role == 'admin'
            )
        return False



class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает действия только для администратора.
    Просмотр доступен всем пользователям.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.role == 'admin'
        )


class IsModerator(BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'moderator'


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает редактировать и удалять контент только автору, модератору или администратору.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_moderator or request.user.is_admin


class IsReadOnly(BasePermission):
    """
    Доступ разрешен для безопасных методов (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
