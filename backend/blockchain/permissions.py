# En blockchain/permissions.py
from rest_framework import permissions

class AdminPermission(permissions.BasePermission):
    """Permiso que solo permite acceso a administradores"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'