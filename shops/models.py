import enum
import random
import string

from django.contrib.auth.models import User
from django.db import models

from accounts.models import UserProfileModel


class ShopType(enum.Enum):
    Food = 1
    Groceries = 2
    Pharmacies = 3


def photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'shops/{0}'.format(res)


def product_photo_upload(instance, filename):
    res = instance.id.join(random.choices(string.ascii_letters, k=20))
    return 'shops/products/{0}'.format(res)


class ShopProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Profile")
    profile_photo = models.ImageField(upload_to=photo_upload)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    shop_type = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class ProductCategoryModel(models.Model):
    shop = models.ForeignKey(to=ShopProfileModel, related_name="products", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()

    class Meta:
        unique_together = ("shop", "sort")

    def __str__(self):
        return self.title


class ProductModel(models.Model):
    currency = models.ForeignKey(to=ProductCategoryModel, related_name="products", on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=product_photo_upload)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    base_price = models.FloatField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class AddOn(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="add_ons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    added_price = models.FloatField()
    currency = models.CharField(max_length=10)

    def __str__(self):
        return self.title


class ShopAddressModel(models.Model):
    shop = models.OneToOneField(to=ShopProfileModel, related_name="address", on_delete=models.CASCADE)
    area = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    special_notes = models.TextField()
    phone_number = models.BigIntegerField()
    land_line_number = models.BigIntegerField()
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6)


class ShopReviewModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, null=True)
    shop = models.ForeignKey(to=ShopProfileModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    time_stamp = models.DateTimeField()

    def __str__(self):
        return self.title


class ProductReviewModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=ProductModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    time_stamp = models.DateTimeField()

    def __str__(self):
        return self.title
