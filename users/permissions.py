#  Copyright (c) Code Written and Tested by Ahmed Emad in 30/12/2019, 17:08
from rest_framework import permissions


class UserProfilePermissions(permissions.BasePermission):
    """The Permission class used by UserProfileView."""
    safe_methods = {'GET', 'POST', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        """Checks if request is safe, if not it checks if
        the user is authenticated and has a valid profile,
        because that account may be other type like a driver, shop or an admin.
        """
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False


class UserAddressPermissions(permissions.BasePermission):
    """The Permission class used by UserAddressView."""

    def has_permission(self, request, view):
        """Checks if the user is authenticated and has a valid profile,
        because that account may be other type like a driver, shop or an admin.
        """
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False
