#  Copyright (c) Code Written and Tested by Ahmed Emad in 06/01/2020, 16:28
from rest_framework import permissions


class ShopProfilePermissions(permissions.BasePermission):
    safe_methods = {'GET', 'POST', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'shop_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.account == request.user:
            return True
        return False
