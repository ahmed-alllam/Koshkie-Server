#  Copyright (c) Code Written and Tested by Ahmed Emad in 07/02/2020, 21:40
from rest_framework import permissions


class DriverProfilePermissions(permissions.BasePermission):
    """The Permission class used by DriverProfileView."""

    safe_methods = {'GET', 'POST', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        """Checks if request is safe, if not it checks if
        the user is authenticated and has a
        valid driver profile,
        because that account may be other type
        like a regular user, shop or an admin.
        """
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'driver_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has permissions to update
        or delete a driver profile"""
        if obj.account == request.user:
            return True
        return False


class DriverReviewPermissions(permissions.BasePermission):
    """The Permission class used by DriverReviewView."""

    safe_methods = {'GET', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        """Checks if the request is in safe methods
        if not checks if the user is authenticated and has a
        valid regular user profile,
        because that account may be other type
        like a driver, shop or an admin.
        """
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has the permissions update or
        delete a review"""
        if obj.user == request.user.profile:
            return True
        return False
