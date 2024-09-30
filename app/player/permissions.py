from rest_framework import permissions
from core.models import League


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to allow read-only access for authenticated users,
    and full access to league admins and additional admins."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        if request.method == 'POST':
            league_id = request.data.get('league')

            if not league_id:
                return False

            try:
                league = League.objects.get(pk=league_id)
            except League.DoesNotExist:
                return False

            return (
                request.user.is_authenticated and
                request.user.is_active and
                (
                    request.user == league.admin or
                    request.user in league.additional_admins.all()
                )
            )

        return True

    def has_object_permission(self, request, view, obj):
        """Object-level permission for RO and admin modifications"""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        league = obj.league

        return request.user == league.admin or (
            request.user in league.additional_admins.all()
        )
