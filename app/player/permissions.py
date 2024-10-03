from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to allow read-only access for authenticated users,
    full access to admins, and allow user to modify their own player profile"""

    def has_permission(self, request, view):
        # Allow authenticated users to make safe (read-only) requests
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow any admin to modify or create player profiles
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and (
                request.user.is_admin or request.method != 'POST'
            )

        return False

    def has_object_permission(self, request, view, obj):
        """Object-level permission for safe methods, own profile,
        or admin modifications."""
        # Allow authenticated users to make safe (read-only) requests
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Allow user to modify their own player profile
        if request.method in [
            'PUT',
            'PATCH'
        ] and obj == request.user.player_profile:
            return True

        # Allow admins to modify any player profile
        return request.user.is_admin
