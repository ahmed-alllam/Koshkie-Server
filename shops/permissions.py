#  Copyright (c) Code Written and Tested by Ahmed Emad in 08/01/2020, 21:55
from rest_framework import permissions

from shops.models import ShopProfileModel, ProductModel, ProductGroupModel, AddOnModel


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


class ShopReviewPermissions(permissions.BasePermission):
    safe_methods = {'GET', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user.profile:
            return True
        return False


class ProductPermissions(permissions.BasePermission):
    safe_methods = {'GET', 'HEAD', 'OPTIONS'}

    def has_permission(self, request, view):
        if request.method in self.safe_methods:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'shop_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if type(obj) == ShopProfileModel:
            if obj.account == request.user:
                return True
        elif type(obj) == ProductModel:
            if obj.shop.account == request.user:
                return True
        return False


class ProductReviewPermissions(permissions.BasePermission):
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


class ProductGroupPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'shop_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if type(obj) == ShopProfileModel:
            if obj.account == request.user:
                return True
        elif type(obj) == ProductGroupModel:
            if obj.shop.account == request.user:
                return True
        return False


class AddOnPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'shop_profile'):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if type(obj) == ProductModel:
            if obj.shop.account == request.user:
                return True
        elif type(obj) == AddOnModel:
            if obj.product.shop.account == request.user:
                return True
        return False
