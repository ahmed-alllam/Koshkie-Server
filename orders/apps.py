#  Copyright (c) Code Written and Tested by Ahmed Emad in 14/02/2020, 14:50

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'orders'

    def ready(self):
        import orders.signals
