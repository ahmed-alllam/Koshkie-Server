import enum
import random
import string

from django.contrib.auth.models import User
from django.db import models

from accounts.models import UserProfileModel


class VehicleType(enum.Enum):
    Car = 1
    Bike = 2
    Motorcycle = 3


def profile_photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'drivers/{0}'.format(res)


class DriverProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    profile_photo = models.ImageField(upload_to=profile_photo_upload)
    is_active = models.BooleanField()
    last_time_online = models.TimeField()
    live_location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    live_location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    vehicle_type = models.PositiveIntegerField()

    def __str__(self):
        return self.user.__str__()


class DriverReview(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    time_stamp = models.TimeField()

    def __str__(self):
        return self.title
