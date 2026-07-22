"""
Custom permission classes for Water Delivery System API.
Enforces role-based access control (RBAC) for different endpoints.
"""
from rest_framework import permissions


class IsAuthenticated(permissions.IsAuthenticated):
    """
    Base permission: User must be authenticated.
    """
    pass


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin (is_staff=True).
    Used for endpoints that only admin users should access.
    """
    message = "Sizda admin huquqi yo'q. Iltimos, administratorga murojaat qiling."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admins to create/update/delete, 
    but everyone authenticated can read.
    """
    message = "Sizda bu amal uchun ruxsat yo'q."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsSuperUser(permissions.BasePermission):
    """
    Permission for superuser-only operations (e.g., system administration).
    """
    message = "Bu operatsiya faqat super-admin uchun."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsAdminUser(permissions.BasePermission):
    """
    Django's built-in check for is_staff flag.
    Alias for clarity.
    """
    message = "Admin ruxsat talab qilinadi."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
