#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/02/2020, 23:44

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        pass
