#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

from django.contrib import admin

from . import models

admin.site.register(models.UserProfileModel)
admin.site.register(models.UserAddressModel)
