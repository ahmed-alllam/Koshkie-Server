#  Copyright (c) Code Written and Tested by Ahmed Emad in 14/02/2020, 17:57
from django.db.models.signals import pre_save
from django.dispatch import receiver
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

from orders.models import OrderAddressModel


@receiver(pre_save, sender=OrderAddressModel)
def add_country_and_city(sender, **kwargs):
    """The receiver called before an order address is saved
    to get the country and city from location coordinates"""

    address = kwargs['instance']
    longitude = address.location_longitude
    latitude = address.location_latitude
    geolocator = Nominatim()
    try:
        location = geolocator.reverse("{}, {}".format(longitude, latitude), language='en')
        address.country = location.raw.get('address', {}).get('country', '')
        address.city = location.raw.get('address', {}).get('state', '') or location.raw.get('address', {}).get('city',
                                                                                                               '')
    except GeocoderTimedOut:
        return add_country_and_city(sender, **kwargs)  # recursion
