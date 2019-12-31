#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/12/2019, 20:06
import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def photo_upload(instance, filename):
    return 'drivers/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class DriverProfileModel(models.Model):
    vehicle_type_choices = [
        ('C', 'Car'),
        ('M', 'Motorcycle'),
        ('B', 'Bike')
    ]

    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver_profile")
    profile_photo = models.ImageField(upload_to=photo_upload, null=True)
    phone_number = models.BigIntegerField()
    is_active = models.BooleanField(default=False)
    last_time_online = models.TimeField(auto_now_add=True)
    live_location_longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, validators=[
        MaxValueValidator(180),
        MinValueValidator(-180)
    ])
    live_location_latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0, validators=[
        MaxValueValidator(90),
        MinValueValidator(-90)
    ])
    vehicle_type = models.CharField(max_length=1, choices=vehicle_type_choices)
    is_busy = models.BooleanField(default=False)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.account.username

    def calculate_rating(self):
        sum_num = 0
        for review in self.reviews.all():
            sum_num = sum_num + review.stars

        avg = sum_num / self.reviews.count()
        self.rating = avg


class DriverReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.CASCADE, related_name='reviews')
    sort = models.PositiveIntegerField()
    stars = models.PositiveIntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0.5)
    ])
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ("driver", "sort")
        ordering = ['sort']
