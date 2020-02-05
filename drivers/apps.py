#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 20:26

from django.apps import AppConfig


class DriversConfig(AppConfig):
    name = 'drivers'

    def ready(self):
        import drivers.signals
