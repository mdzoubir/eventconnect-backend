from rest_framework import permissions


class IsOrganizerReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only organizers to view contacts.
    """

    def has_permission(self, request, view):
        # Allow POST requests for anyone (to create contacts)
        if request.method == 'POST':
            return True

        # Check if user is authenticated and is an organizer for GET requests
        return (
                request.user.is_authenticated and
                hasattr(request.user, 'role') and
                request.user.role == 'organizer'
        )

    def has_object_permission(self, request, view, obj):
        # Only allow GET for organizers, deny other methods
        return request.method in permissions.SAFE_METHODS

from rest_framework import permissions

class IsAdminOrOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'organizer']


# Custom permission class for user ownership
class IsOwnerOrAllowed(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it
    """

    def has_object_permission(self, request, view, obj):
        # Allow if user is admin
        if request.user.is_staff or request.user.role in ['admin', 'organizer']:
            return True

        # Allow if user is the owner
        return obj.id == request.user.id