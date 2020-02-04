#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 00:39

from django.contrib import admin
from django.contrib.auth.models import Group

from . import models

admin.site.site_header = 'Koshkie Admin Dashboard'  # header for the admin site


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for users model"""

    list_display = ('username', 'profile_photo', 'phone_number')

    def username(self, obj):
        return obj.account.username


class UserAddressAdmin(admin.ModelAdmin):
    """Admin for users addresses model"""

    list_display = ('title', 'user', 'country', 'city', 'area', 'type', 'phone_number')
    list_filter = ('country', 'city')
    readonly_fields = ('sort', 'country', 'city')

    def user(self, obj):
        """returns the username of the address's user"""
        return obj.user.account.username

    def phone_number(self, obj):
        """returns the phone number of the address's user"""
        return obj.user.phone_number


admin.site.register(models.UserProfileModel, UserProfileAdmin)
admin.site.register(models.UserAddressModel, UserAddressAdmin)
admin.site.unregister(Group)  # unregister default django model group
