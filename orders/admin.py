from django.contrib import admin

# Register your models here.
from orders.models import OrderModel

admin.site.register(OrderModel)
