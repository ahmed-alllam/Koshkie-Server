#  Copyright (c) Code Written and Tested by Ahmed Emad in 11/02/2020, 20:13

from django.contrib import admin
from geopy import Nominatim

from drivers.models import DriverReviewModel, DriverProfileModel


class DriverProfileAdmin(admin.ModelAdmin):
    """Admin for drivers model"""

    list_display = ('username', 'profile_photo', 'phone_number', 'vehicle_type', 'rating')
    search_fields = ('account__username', 'phone_number')
    ordering = ('account__username',)
    list_select_related = ('account',)
    readonly_fields = ('country', 'city', 'rating', 'last_time_online', 'is_available')

    def username(self, obj):
        """returns the username of the user"""
        return obj.account.username

    def city(self, obj):
        """returns the city of the last recorded location for driver"""
        longitude = obj.live_location_longitude
        latitude = obj.live_location_latitude
        geolocator = Nominatim()
        try:
            location = geolocator.reverse("{}, {}".format(longitude, latitude), language='en')
            return location.raw.get('address', {}).get('state', '') or location.raw.get('address', {}).get('city', '')
        except Exception:
            return ''

    def country(self, obj):
        """returns the country of the last recorded location for driver"""
        longitude = obj.live_location_longitude
        latitude = obj.live_location_latitude
        geolocator = Nominatim()
        try:
            location = geolocator.reverse("{}, {}".format(longitude, latitude), language='en')
            return location.raw.get('address', {}).get('country', '')
        except Exception:
            return ''


class DriverReviewAdmin(admin.ModelAdmin):
    """Admin for driver reviews model"""

    list_display = ('user', 'driver', 'stars')
    search_fields = ('driver__account__username', 'user__account__username')
    ordering = ('time_stamp',)
    list_select_related = ('user__account', 'driver__account')
    readonly_fields = ('sort', 'time_stamp')

    def user(self, obj):
        """returns the username of the review's user"""
        return obj.user.account.username

    def driver(self, obj):
        """returns the username of the reivew's driver"""
        return obj.driver.account.username


admin.site.register(DriverProfileModel, DriverProfileAdmin)
admin.site.register(DriverReviewModel, DriverReviewAdmin)
