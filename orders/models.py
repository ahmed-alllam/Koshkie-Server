from django.db import models

from accounts.models import UserProfileModel, UserAddressModel
from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel, ProductModel, AddOn, OptionGroupModel


class OrderModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders', null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders',
                               null=True)
    shops = models.ManyToManyField(to=ShopProfileModel, related_name='served_orders')
    ordered_at = models.DateTimeField()
    shipping_address = models.ForeignKey(to=UserAddressModel, on_delete=models.SET_NULL, null=True)
    arrived = models.BooleanField(default=False)

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_item_price()
        return total


class OrderItemModel(models.Model):
    order = models.ForeignKey(to=OrderModel, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(to=ProductModel, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    add_ons = models.ManyToManyField(to=AddOn)
    option_groups = models.ManyToManyField(to=OptionGroupModel)

    def __str__(self):
        return self.product.title

    def get_add_ons_price(self):
        total = 0
        for add_on in self.add_ons.all():
            total += add_on.added_price
        return total

    def get_item_price(self):
        return (self.product.base_price * self.quantity) + self.get_add_ons_price()
