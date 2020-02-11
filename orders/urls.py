#  Copyright (c) Code Written and Tested by Ahmed Emad in 11/02/2020, 22:16
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from orders.views import OrderView

orders_router = DefaultRouter()
orders_router.register('', OrderView, basename='orders')

app_name = 'orders'

urlpatterns = [
    path('', include(orders_router.urls))
]
