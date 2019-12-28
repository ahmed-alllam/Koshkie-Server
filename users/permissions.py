#  Copyright (c) Code Written and Tested by Ahmed Emad in 28/12/2019, 22:43
from rest_framework import permissions


class HasProfile(permissions.BasePermission):
    """The Permission class used by UserProfileView and UserAddressView"""

    def has_permission(self, request, view):
        """Checks if the user has a valid profile, because that account may
        be other type like a driver, shop or an admin
        """
        if hasattr(request.user, 'profile'):
            return True
        return False
