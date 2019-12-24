#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

import random
import string

from django.contrib.auth.models import User
from django.db import models


def photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'users/{0}'.format(res)


class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_photo = models.ImageField(upload_to=photo_upload, null=True)
    phone_number = models.BigIntegerField(null=True)
    favourite_products = models.ManyToManyField(to='shops.ProductModel')

    def __str__(self):
        return self.user.username


class UserAddressModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, related_name="addresses", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    type = models.CharField(max_length=15)  # house , office or apartment
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    floor = models.PositiveIntegerField(default=1)
    apartment_no = models.PositiveIntegerField(default=1)
    special_notes = models.TextField(blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.title
