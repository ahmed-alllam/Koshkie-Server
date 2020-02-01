#  Copyright (c) Code Written and Tested by Ahmed Emad in 01/02/2020, 18:18
import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Avg

from . import unique_slugify


def shop_photo_upload(instance, filename):
    return 'shops/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


def product_photo_upload(instance, filename):
    return 'shops/products/{0}.{1}'.format(uuid.uuid4().hex, os.path.splitext(filename))


class ShopProfileModel(models.Model):
    shop_type_choices = [
        ('F', 'Food'),
        ('G', 'Groceries'),
        ('P', 'Pharmacy')
    ]

    currencies = [
        ('$', 'Dollar'),
        ('€', 'Euro'),
        ('egp', 'Egyptian Pound')
    ]

    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shop_profile")
    profile_photo = models.ImageField(upload_to=shop_photo_upload)
    cover_photo = models.ImageField(upload_to=shop_photo_upload)
    phone_number = models.BigIntegerField()
    description = models.TextField()
    shop_type = models.CharField(max_length=1, choices=shop_type_choices)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=2)
    is_active = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, choices=currencies)
    minimum_charge = models.FloatField(default=0)
    delivery_fee = models.FloatField()
    vat = models.FloatField(default=0, max_length=2, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    time_to_prepare = models.IntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)

        super(ShopProfileModel, self).save(*args, **kwargs)

    def calculate_rating(self):
        self.rating = self.reviews.aggregate(Avg('stars'))['stars__avg'] or 0

    def resort_reviews(self, sort):
        self.reviews.filter(sort__gt=sort).update(sort=F('sort') - 1)

    def resort_product_groups(self, sort):
        product_groups = self.product_groups.filter(sort__gt=sort)
        for product_group in product_groups:
            product_group.sort -= 1
            product_group.save()

    def update_attrs(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError("Failed to update non existing attribute {}.{}".format(
                    self.__class__.__name__, key))
        self.save()


class ShopTagsModel(models.Model):
    shop = models.ForeignKey(ShopProfileModel, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=10)


class ProductGroupModel(models.Model):
    shop = models.ForeignKey(to=ShopProfileModel, related_name="product_groups", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = (("shop", "sort"), ("shop", "title"))
        ordering = ['sort']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = ProductGroupModel.objects.filter(shop=self.shop).count()
            self.sort = latest_sort + 1

        super(ProductGroupModel, self).save(*args, **kwargs)


class ProductModel(models.Model):
    shop = models.ForeignKey(to=ShopProfileModel, related_name="products", on_delete=models.CASCADE)
    product_group = models.ForeignKey(to=ProductGroupModel, related_name="products",
                                      on_delete=models.CASCADE, null=True)
    photo = models.ImageField(upload_to=product_photo_upload)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    rating = models.DecimalField(default=0, decimal_places=1, max_digits=2)
    is_available = models.BooleanField(default=True)
    is_offer = models.BooleanField(default=False)
    num_sold = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("shop", "slug")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)

        super(ProductModel, self).save(*args, **kwargs)

    def calculate_rating(self):
        self.rating = self.reviews.aggregate(Avg('stars'))['stars__avg'] or 0

    def resort_reviews(self, sort):
        self.reviews.filter(sort__gt=sort).update(sort=F('sort') - 1)

    def resort_addons(self, sort):
        addons = self.add_ons.filter(sort__gt=sort)
        for addon in addons:
            addon.sort -= 1
            addon.save()

    def resort_option_groups(self, sort):
        option_groups = self.option_groups.filter(sort__gt=sort)
        for option_group in option_groups:
            option_group.sort -= 1
            option_group.save()


class OptionGroupModel(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="option_groups", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField(null=True)
    changes_price = models.BooleanField(default=False)

    class Meta:
        unique_together = ("product", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = OptionGroupModel.objects.filter(product=self.product).count()
            self.sort = latest_sort + 1

        super(OptionGroupModel, self).save(*args, **kwargs)

    def resort_options(self, sort):
        options = self.options.filter(sort__gt=sort)
        for option in options:
            option.sort -= 1
            option.save()


class OptionModel(models.Model):
    option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.CASCADE, related_name="options")
    title = models.CharField(max_length=255)
    sort = models.PositiveIntegerField(null=True)
    price = models.FloatField(null=True)

    class Meta:
        unique_together = ("option_group", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = OptionModel.objects.filter(option_group=self.option_group).count()
            self.sort = latest_sort + 1

        super(OptionModel, self).save(*args, **kwargs)


class AddOnModel(models.Model):
    product = models.ForeignKey(to=ProductModel, related_name="add_ons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    added_price = models.FloatField()
    sort = models.PositiveIntegerField(null=True)

    class Meta:
        unique_together = ("product", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = AddOnModel.objects.filter(product=self.product).count()
            self.sort = latest_sort + 1

        super(AddOnModel, self).save(*args, **kwargs)


class RelyOn(models.Model):
    option_group = models.OneToOneField(to=OptionGroupModel, on_delete=models.CASCADE, related_name='rely_on')
    choosed_option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.CASCADE)
    option = models.ForeignKey(to=OptionModel, on_delete=models.CASCADE)


class ShopAddressModel(models.Model):
    shop = models.OneToOneField(to=ShopProfileModel, related_name="address", on_delete=models.CASCADE)
    area = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    special_notes = models.TextField(blank=True)
    location_longitude = models.FloatField(default=0, validators=[
        MaxValueValidator(180),
        MinValueValidator(-180)
    ])
    location_latitude = models.FloatField(default=0, validators=[
        MaxValueValidator(90),
        MinValueValidator(-90)
    ])

    def update_attrs(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError("Failed to update non existing attribute {}.{}".format(
                    self.__class__.__name__, key))
        self.save(force_update=True)


class ShopReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    shop = models.ForeignKey(to=ShopProfileModel, on_delete=models.CASCADE, related_name='reviews')
    sort = models.PositiveIntegerField()
    stars = models.FloatField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0.5)
    ])
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("shop", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = ShopReviewModel.objects.filter(shop=self.shop).count()
            self.sort = latest_sort + 1

        super(ShopReviewModel, self).save(*args, **kwargs)


class ProductReviewModel(models.Model):
    user = models.ForeignKey(to='users.UserProfileModel', on_delete=models.SET_NULL, null=True)
    sort = models.PositiveIntegerField()
    product = models.ForeignKey(to=ProductModel, on_delete=models.CASCADE, related_name='reviews')
    stars = models.FloatField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0.5)
    ])
    text = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "sort")
        ordering = ['sort']

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.pk is None:
            latest_sort = ProductReviewModel.objects.filter(product=self.product).count()
            self.sort = latest_sort + 1

        super(ProductReviewModel, self).save(*args, **kwargs)
