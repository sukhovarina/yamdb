from rest_framework import permissions


class AdminModOwnerOrReadOnly(permissions.BasePermission):      #для отзывов, комментариев, оценок
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author==request.user
            or request.user.role=='admin'
            or request.user.role=='moderator'
        )


class AdminOrReadOnly(permissions.BasePermission):      #для списка произведений, категорий и жанров
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user.role=='admin'
        )


class AdminOnly(permissions.BasePermission):        #для списка юзеров
    def has_permission(self, request, view):
        return (
            request.user.is_staff
            or request.user.role=='admin'
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_staff
            or request.user.role=='admin'
        )


class OwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
