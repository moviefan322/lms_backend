from rest_framework import permissions
from core.models import League  # Import the League model to query it


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to allow read-only access for authenticated users,
    and full access to league admins and additional admins."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Skip league admin check for POST (league creation)
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.is_admin

        # For other write operations, ensure the user is an admin or additional admin
        league = None
        if 'pk' in view.kwargs:
            league = League.objects.get(pk=view.kwargs['pk'])
        
        return request.user.is_authenticated and (
            request.user == league.admin or 
            request.user in league.additional_admins.all()
        )


    def has_object_permission(self, request, view, obj):
        """Object-level permission for read-only access and admin-only modifications"""
        # Allow read access to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Only allow admin or additional admins to modify the object
        return request.user == obj.admin or request.user in obj.additional_admins.all()
