#  Copyright (c) Code Written and Tested by Ahmed Emad in 16/01/2020, 17:53
from rest_framework import permissions


class OrderPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if hasattr(request.user, 'profile') or hasattr(request.user, 'driver_profile') or hasattr(request.user,
                                                                                                  'shop_profile'):
            return True

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'profile'):
            if obj.user == request.user.profile:
                return True

        if hasattr(request.user, 'driver_profile'):
            if obj.driver == request.user.driver_profile:
                return True

        if hasattr(request.user, 'shop_profile'):
            if obj.shops.filter(request.user.shop_profile).exists():
                return True

        return False
