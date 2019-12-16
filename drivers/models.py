import enum
import random
import string

from django.contrib.auth.models import User
from django.db import models


class VehicleType(enum.Enum):
    Car = 1
    Bike = 2
    Motorcycle = 3


def photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'drivers/{0}'.format(res)


class DriverProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    profile_photo = models.ImageField(upload_to=photo_upload, null=True)
    phone_number = models.BigIntegerField()
    is_active = models.BooleanField(default=False)
    last_time_online = models.TimeField()
    live_location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    live_location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    vehicle_type = models.PositiveIntegerField()
    is_busy = models.BooleanField(default=False)
    rating = models.FloatField()

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
