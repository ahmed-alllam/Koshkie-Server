#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 20:11

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from orders.models import OrderModel, OrderItemModel, Choice, OrderAddressModel, OrderItemsGroupModel


class OrderAdmin(ModelAdmin):
    """admin customization for orders model"""

    list_display = ('__str__', 'user', 'driver', 'status', 'final_price', 'ordered_at',
                    'country', 'city')
    search_fields = ('user__account__username', 'driver__account__username',
                     'user__phone_number', 'driver__phone_number')
    ordering = ('ordered_at',)
    list_select_related = ('user__account', 'driver__account', 'shipping_address')
    list_filter = ('shipping_address__country', 'shipping_address__city')

    def user(self, obj):
        """returns the username of the user"""
        return obj.user.account.username

    def driver(self, obj):
        """returns the username of the driver"""
        return obj.driver.account.username

    def country(self, obj):
        """returns the country of the order"""
        return obj.shipping_address.country

    def city(self, obj):
        """returns the city of the order"""
        return obj.shipping_address.city


class OrderItemsGroupAdmin(ModelAdmin):
    """admin customization for orders items group model"""

    list_display = ('order', 'shop')


class OrderItemAdmin(ModelAdmin):
    """admin customization for order items model"""

    list_display = ('product', 'quantity', 'price')

    def product(self, obj):
        """returns the name of the product"""
        return obj.product.name


class OrderAddressAdmin(ModelAdmin):
    """admin customization for orders address model"""

    list_display = ('user', 'country', 'city', 'area', 'type', 'phone_number')
    list_filter = ('country', 'city')
    search_fields = ('city', 'order__user__phone_number')
    ordering = ('city',)
    list_select_related = ('order__user__account',)
    readonly_fields = ('country', 'city')

    def user(self, obj):
        """returns the username of the address's user"""
        return obj.order.user.account.username

    def phone_number(self, obj):
        """returns the phone number of the address's user"""
        return obj.order.user.phone_number


class ChoiceAdmin(ModelAdmin):
    """admin customization for orders item choice model"""

    list_display = ('order', 'shop', 'product',
                    'option_group', 'choosed_option')
    list_select_related = ('order_item__item_group__order', 'order_item__product__shop')

    def order(self, obj):
        """returns the orders pk"""
        return obj.order_item.item_group.order.pk

    def shop(self, obj):
        """returns the shop of the item"""
        return obj.order_item.product.shop

    def product(self, obj):
        """returns the product of the item"""
        return obj.order_item.product


admin.site.register(OrderModel, OrderAdmin)
admin.site.register(OrderItemsGroupModel, OrderItemsGroupAdmin)
admin.site.register(OrderItemModel, OrderItemAdmin)
admin.site.register(OrderAddressModel, OrderAddressAdmin)
admin.site.register(Choice, ChoiceAdmin)
