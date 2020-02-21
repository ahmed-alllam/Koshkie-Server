#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 20:11
from rest_framework import permissions


class OrderPermissions(permissions.BasePermission):
    """The Permission class used by OrderView."""

    def has_permission(self, request, view):
        """Checks if user is authenticated, if not returns false.
        if the request is GET it check if the user has a valid profile of any type,
        if the request is POST it check if the user has a valid regular User profile
        (because only users can add orders),
        if the request is PATCH it check if the user has a valid driver profile,
        (because only drivers can change the state of the order)
        """

        if not request.user.is_authenticated:
            return False

        if request.method == 'GET':
            if hasattr(request.user, 'profile') or hasattr(request.user, 'driver_profile') or hasattr(request.user,
                                                                                                      'shop_profile'):
                return True

        if request.method == 'POST':
            if hasattr(request.user, 'profile'):
                return True

        if request.method == 'PATCH':
            if hasattr(request.user, 'driver_profile'):
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """Checks if the user has permissions to get or update a certain order.
        if the request is GET, it check if the user is either the user who
        ordered it or the driver or one of the shops in that order's products list
        If the request id PATCH it checks if the user is the order's driver.
        """

        if request.method == 'GET':
            if hasattr(request.user, 'profile'):
                if obj.user == request.user.profile:
                    return True

            if hasattr(request.user, 'driver_profile'):
                if obj.driver == request.user.driver_profile:
                    return True

            if hasattr(request.user, 'shop_profile'):
                if obj.shops.filter(pk=request.user.shop_profile.pk).exists():
                    return True

            return False

        if request.method == 'PATCH':
            if hasattr(request.user, 'driver_profile'):
                if obj.driver == request.user.driver_profile:
                    return True
            return False
