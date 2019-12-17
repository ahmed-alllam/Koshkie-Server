import enum
import random
import string

from django.contrib.auth.models import User
from django.db import models


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
    profile_photo = models.ImageField(upload_to=photo_upload)
    phone_number = models.BigIntegerField()
    shop_type = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    rating = models.FloatField()
    is_active = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    currency = models.CharField(max_length=10, default='')
    minimum_charge = models.FloatField(default=0)
    delivery_fee = models.FloatField()
    vat = models.FloatField(default=0)
    opens_at = models.TimeField(auto_now=False, auto_now_add=False)
    closes_at = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.name


class ProductGroupModel(models.Model):
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
    product_group = models.ForeignKey(to=ProductGroupModel, related_name="products", on_delete=models.CASCADE)
    base_price = models.FloatField()
    rating = models.FloatField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class OptionGroupModel(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="option_groups", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()
    changes_price = models.BooleanField(default=False)

    class Meta:
        unique_together = ("product", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title


class OptionModel(models.Model):
    option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.CASCADE, related_name="options")
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField()
    price = models.FloatField()

    class Meta:
        unique_together = ("option_group", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title


class AddOn(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="add_ons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    added_price = models.FloatField()
    sort = models.PositiveIntegerField()

    class Meta:
        unique_together = ("product", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title


class RelyOn(models.Model):
    option_group = models.OneToOneField(to=OptionGroupModel, on_delete=models.CASCADE, null=True, default=None,
                                        related_name='rely_on')
    choosed_option_group = models.OneToOneField(to=OptionGroupModel, on_delete=models.CASCADE)
    option = models.OneToOneField(to=OptionModel, on_delete=models.CASCADE)


class ShopAddressModel(models.Model):
    shop = models.OneToOneField(to=ShopProfileModel, related_name="address", on_delete=models.CASCADE)
    area = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    special_notes = models.TextField(blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6)


class ShopReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    shop = models.ForeignKey(to=ShopProfileModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProductReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=ProductModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
