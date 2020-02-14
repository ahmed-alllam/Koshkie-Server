#  Copyright (c) Code Written and Tested by Ahmed Emad in 14/02/2020, 14:50
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel, ProductModel, AddOnModel, OptionGroupModel, OptionModel
from users.models import UserProfileModel


class OrderModel(models.Model):
    """The Model of the Orders."""

    status = (
        ('C', 'confirmed'),
        ('P', 'picked'),
        ('D', 'delivered')
    )

    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders', null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders',
                               null=True)
    shops = models.ManyToManyField(to=ShopProfileModel, related_name='served_orders')
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=status, default='C')
    arrived = models.BooleanField(default=False)
    final_price = models.FloatField()
    subtotal = models.FloatField()
    delivery_fee = models.FloatField()
    vat = models.FloatField()


class OrderItemsGroupModel(models.Model):
    """The Model of the Order's items' groups."""

    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='item_groups', null=True)
    shop = models.ForeignKey(ShopProfileModel, on_delete=models.SET_NULL, null=True)


class OrderItemModel(models.Model):
    """The Model of the Orders item."""

    item_group = models.ForeignKey(to=OrderItemsGroupModel, on_delete=models.CASCADE,
                                   related_name='items', null=True)
    product = models.ForeignKey(to=ProductModel, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    add_ons = models.ManyToManyField(to=AddOnModel)
    special_request = models.TextField(blank=True)
    price = models.FloatField(default=0)

    def __str__(self):
        return self.product.title

    def get_add_ons_price(self):
        """Calculates and adds all add-ons prices"""
        total = 0
        for add_on in self.add_ons.all():
            total += add_on.added_price
        return total

    def get_item_price(self):
        """Calculates the item's price"""
        product_price = self.product.price
        for choice in self.choices.all():
            if choice.option_group.changes_price:
                product_price = choice.choosed_option.price
        return (product_price + self.get_add_ons_price()) * self.quantity

    def calculate_vat(self):
        """Calculates the VAT for an item
        given the shop's VAT percentage"""
        return self.get_item_price() * (self.product.shop.vat / 100)


class OrderAddressModel(models.Model):
    """The Model of the Order's Address, it is used
    as an alias to user address because the user
    may delete or change his addresses list in the future
    which can result in wrong or no data for that past order."""

    address_type_choices = [
        ('H', 'House'),
        ('O', 'Office'),
        ('A', 'Apartment')
    ]
    order = models.OneToOneField(OrderModel, on_delete=models.CASCADE,
                                 related_name='shipping_address')
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


class Choice(models.Model):
    """The Model of the Order's item choice."""

    order_item = models.ForeignKey(to=OrderItemModel, related_name='choices',
                                   on_delete=models.CASCADE)
    option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.SET_NULL, null=True)
    choosed_option = models.ForeignKey(to=OptionModel, on_delete=models.SET_NULL, null=True)
