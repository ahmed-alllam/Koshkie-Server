#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 20:26

from django.contrib import admin

from drivers.models import DriverReviewModel, DriverProfileModel

admin.site.register(DriverProfileModel)
admin.site.register(DriverReviewModel)
