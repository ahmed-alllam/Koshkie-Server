#  Copyright (c) Code Written and Tested by Ahmed Emad in 07/02/2020, 21:40
import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg


def photo_upload(instance, filename):
    """Gives a unique path to the saved photo in models.
        Arguments:
            instance: the photo itself, it is not used in this
                      function but it's required by django.
            filename: the name of the photo sent by user, it's
                      used here to get the format of the file.

        Returns:
            The unique path that the file will be stored in the DB.
        """
    return 'drivers/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class DriverProfileModel(models.Model):
    """The Model of the Driver Profile."""

    vehicle_type_choices = [
        ('C', 'Car'),
        ('M', 'Motorcycle'),
        ('B', 'Bike')
    ]

    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    profile_photo = models.ImageField(upload_to=photo_upload)
    phone_number = models.BigIntegerField()
    is_active = models.BooleanField(default=False)  # is evaluated and confirmed in person from the company (not fake)
    is_available = models.BooleanField(default=False)  # is ready for orders at the moment
    last_time_online = models.DateTimeField(auto_now_add=True)
    live_location_longitude = models.FloatField(default=0, validators=[
        MaxValueValidator(180),
        MinValueValidator(-180)
    ])
    live_location_latitude = models.FloatField(default=0, validators=[
        MaxValueValidator(90),
        MinValueValidator(-90)
    ])
    vehicle_type = models.CharField(max_length=1, choices=vehicle_type_choices)
    is_busy = models.BooleanField(default=False)  # on an order or not
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=2)

    def __str__(self):
        return self.account.username

    def calculate_rating(self):
        """Calculates the average rating of the driver from their reviews"""

        self.rating = self.reviews.aggregate(Avg('stars')).get('stars__avg', 0)


class DriverReviewModel(models.Model):
    """The Model of the Driver's Reviews."""

    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.CASCADE, related_name='reviews')
    sort = models.PositiveIntegerField()
    stars = models.FloatField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0.5)
    ])
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("driver", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.text
