#  Copyright (c) Code Written and Tested by Ahmed Emad in 03/02/2020, 00:49

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals
