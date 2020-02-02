#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/02/2020, 23:44

from django.contrib import admin

from . import models

admin.site.register(models.UserProfileModel)
admin.site.register(models.UserAddressModel)
# todo
