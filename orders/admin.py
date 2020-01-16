#  Copyright (c) Code Written and Tested by Ahmed Emad in 16/01/2020, 17:53

from django.contrib import admin

from orders.models import OrderModel, OrderItemModel, Choice, OrderItemsGroupModel, OrderAddressModel

admin.site.register(OrderModel)
admin.site.register(OrderItemsGroupModel)
admin.site.register(OrderItemModel)
admin.site.register(OrderAddressModel)
admin.site.register(Choice)
