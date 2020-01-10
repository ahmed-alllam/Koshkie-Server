#  Copyright (c) Code Written and Tested by Ahmed Emad in 10/01/2020, 18:25
from rest_framework import permissions


class OrderPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        pass

    def has_object_permission(self, request, view, obj):
        pass
