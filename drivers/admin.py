from django.contrib import admin

# Register your models here.
from drivers.models import DriverReviewModel, DriverProfileModel

admin.site.register(DriverProfileModel)
admin.site.register(DriverReviewModel)
