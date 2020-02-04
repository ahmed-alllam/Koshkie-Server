#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/02/2020, 19:34

from django.contrib import admin

from . import models

admin.site.register(models.UserProfileModel)
admin.site.register(models.UserAddressModel)
