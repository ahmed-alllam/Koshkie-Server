from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.UserProfileModel)
admin.site.register(models.UserAddressModel)
