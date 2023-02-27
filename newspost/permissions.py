from rest_framework import permissions
from .models import CustomUser

class IsReporterOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow reporters and admins to edit news posts.
    Users can only view news posts.
    """
    def has_permission(self, request, view):
        # allow anyone to view the list of news posts
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # only allow reporters and admins to create new news posts
        if request.user.is_authenticated and request.user.is_verified and request.user.role == CustomUser.REPORTER:
            return True

        # deny access to users who are not reporters or admins
        return False

    def has_object_permission(self, request, view, obj):
        # allow reporters and admins to edit news posts they created
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == CustomUser.REPORTER or
            request.user.is_superuser
        )

class UserCanLikePost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.is_authenticated and request.user.role == 'User'
        return True
