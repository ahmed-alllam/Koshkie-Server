from django.db import models

from accounts.models import UserProfileModel, UserAddressModel
from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel


class OrderModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders', null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders',
                               null=True)
    shops = models.ManyToManyField(to=ShopProfileModel, related_name='served_orders')
    ordered_at = models.DateTimeField()
    shipping_address = models.OneToOneField(to=UserAddressModel, on_delete=models.SET_NULL, null=True)
    arrived = models.BooleanField(default=False)
