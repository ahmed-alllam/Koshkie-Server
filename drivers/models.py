#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019
import os
import uuid

from django.contrib.auth.models import User
from django.db import models


def photo_upload(instance, filename):
    return 'drivers/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class DriverProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    profile_photo = models.ImageField(upload_to=photo_upload, null=True)
    phone_number = models.BigIntegerField()
    is_active = models.BooleanField(default=False)
    last_time_online = models.TimeField(auto_now_add=True)
    live_location_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    live_location_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    vehicle_type = models.CharField(max_length=20)
    is_busy = models.BooleanField(default=False)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username


class DriverReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
