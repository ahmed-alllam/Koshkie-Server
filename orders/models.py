from django.db import models

from accounts.models import UserProfileModel
from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel


class OrderModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders', null=True)
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders',
                               null=True)
    shops = models.ManyToManyField(to=ShopProfileModel, related_name='served_orders')
    ordered_at = models.DateTimeField()
    arrived = models.BooleanField(default=False)
