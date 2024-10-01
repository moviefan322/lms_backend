from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to allow read-only access for authenticated users,
    and full access to admins."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow any admin to create a player
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.is_admin

        if request.method == 'PUT':
            return request.user.is_authenticated and request.user.is_admin

        if request.method == 'PATCH':
            return request.user.is_authenticated and request.user.is_admin

        if request.method == 'DELETE':
            return request.user.is_authenticated and request.user.is_admin

        return False

    def has_object_permission(self, request, view, obj):
        """Object-level permission for safe methods or admin modifications."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow admin to modify the object
        return request.user.is_admin
