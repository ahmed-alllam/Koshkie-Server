#  Copyright (c) Code Written and Tested by Ahmed Emad in 08/01/2020, 21:55

from django.db import models

from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel, ProductModel, AddOnModel, OptionGroupModel, OptionModel
from users.models import UserProfileModel, UserAddressModel


class OrderModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders', null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders',
                               null=True)
    shops = models.ManyToManyField(to=ShopProfileModel, related_name='served_orders')
    ordered_at = models.DateTimeField(auto_now_add=True)
    shipping_address = models.ForeignKey(to=UserAddressModel, on_delete=models.SET_NULL, null=True)
    arrived = models.BooleanField(default=False)
    final_price = models.FloatField()
    subtotal = models.FloatField()
    delivery_fee = models.FloatField()
    vat = models.FloatField(default=0)


class OrderItemModel(models.Model):
    order = models.ForeignKey(to=OrderModel, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(to=ProductModel, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    add_ons = models.ManyToManyField(to=AddOnModel)
    special_request = models.TextField(blank=True)

    def __str__(self):
        return self.product.title

    def get_add_ons_price(self):
        total = 0
        for add_on in self.add_ons.all():
            total += add_on.added_price
        return total

    def get_item_price(self):
        product_price = self.product.price
        for choice in self.choices.all():
            if choice.option_group.changes_price:
                product_price = choice.choosed_option.price
        return (product_price + self.get_add_ons_price()) * self.quantity

    def get_shop(self):
        return self.product.product_group.shop

    def calculate_vat(self):
        return self.get_item_price() * (self.get_shop().vat / 100)


class Choice(models.Model):
    order_item = models.ForeignKey(to=OrderItemModel, related_name='choices', on_delete=models.CASCADE)
    option_group = models.ForeignKey(to=OptionGroupModel, on_delete=models.CASCADE)
    choosed_option = models.ForeignKey(to=OptionModel, on_delete=models.CASCADE)
