#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False
