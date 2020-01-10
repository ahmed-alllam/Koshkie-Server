#  Copyright (c) Code Written and Tested by Ahmed Emad in 10/01/2020, 18:25

from django.contrib import admin

from orders.models import OrderModel, OrderItemModel, Choice

admin.site.register(OrderModel)
admin.site.register(OrderItemModel)
admin.site.register(Choice)
