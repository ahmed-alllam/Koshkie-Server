#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 00:39
import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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

    return 'users/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class UserProfileModel(models.Model):
    """The Model of the User Profile."""

    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_photo = models.ImageField(upload_to=photo_upload, null=True)
    phone_number = models.BigIntegerField()

    def __str__(self):
        return self.account.username


class UserAddressModel(models.Model):
    """The Model of the User's address."""

    address_type_choices = [
        ('H', 'House'),
        ('O', 'Office'),
        ('A', 'Apartment')
    ]

    user = models.ForeignKey(to=UserProfileModel, related_name="addresses", on_delete=models.CASCADE)
    sort = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    country = models.CharField(max_length=255, blank=True)  # only used in the admin dashboard
    city = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=address_type_choices)
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    floor = models.PositiveIntegerField(default=1)
    apartment_no = models.PositiveIntegerField(default=1)
    special_notes = models.TextField(blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[
        MaxValueValidator(180),
        MinValueValidator(-180)
    ])
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, validators=[
        MaxValueValidator(90),
        MinValueValidator(-90)
    ])

    class Meta:
        unique_together = ("user", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title
