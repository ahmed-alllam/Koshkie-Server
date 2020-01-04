#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/01/2020, 12:48
from rest_framework import permissions


class DriverProfilePermissions(permissions.BasePermission):
    safe_methods = {'GET', 'POST', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'driver_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.account == request.user:
            return True
        return False


class DriverReviewPermissions(permissions.BasePermission):
    safe_methods = {'GET', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user.account == request.user:
            return True
        return False
