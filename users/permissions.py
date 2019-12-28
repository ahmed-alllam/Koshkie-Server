#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        from users.views import UserAddressView
        if view == UserAddressView:
            return obj.user.account == request.user
        return obj.account == request.user
