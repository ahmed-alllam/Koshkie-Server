from django.db import models
from accounts.models import UserProfileModel
from drivers.models import DriverProfileModel
from shops.models import ShopProfileModel


class OrderModel(models.Model):
    user = models.ForeignKey(to=UserProfileModel, on_delete=models.SET_NULL, related_name='orders')
    driver = models.ForeignKey(to=DriverProfileModel, on_delete=models.SET_NULL, related_name='served_orders')
    shops = models.ManyToManyField(to=ShopProfileModel)
    ordered_at = models.TimeField()
    arrived = models.BooleanField(default=False)
