from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Разрешение: только владелец может изменять/удалять свои привычки"""
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение: владелец - полный доступ, остальные - только чтение"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
