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
    extra = ''
    if type(instance) is ProductModel:
        extra = 'products/'
    return 'shops/{0}{1}'.format(res, extra)


class ShopProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Profile")
    favourite_user = models.ManyToManyField(to=UserProfileModel)
    profile_photo = models.ImageField(upload_to=photo_upload)
    shop_type = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    currency = models.CharField(max_length=10, default='')
    minimum_charge = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProductCategoryModel(models.Model):
    shop = models.ForeignKey(to=ShopProfileModel, related_name="products", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()

    class Meta:
        unique_together = ("shop", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title


class ProductModel(models.Model):
    photo = models.ImageField(upload_to=photo_upload)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(to=ProductCategoryModel, related_name="products", on_delete=models.CASCADE)
    base_price = models.FloatField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class OptionGroupModel(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="option_groups", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    changes_price = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class OptionModel(models.Model):
    option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.CASCADE, related_name="options")
    title = models.CharField(max_length=255)
    price = models.FloatField()

    def __str__(self):
        return self.title


class AddOn(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="add_ons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    added_price = models.FloatField()

    def __str__(self):
        return self.title


class RelyOn(models.Model):
    add_on = models.ForeignKey(AddOn, on_delete=models.CASCADE, related_name="rely_ons", null=True, default=None)
    option_group = models.ForeignKey(OptionGroupModel, on_delete=models.CASCADE,
                                     related_name="rely_ons", null=True, default=None)
    choosed_option_group = models.ForeignKey(OptionGroupModel, on_delete=models.CASCADE)
    option = models.ForeignKey(to=OptionModel, on_delete=models.CASCADE)


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
