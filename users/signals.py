#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 17:27
from django.db.models import F
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

from users.models import UserProfileModel, UserAddressModel


@receiver(post_delete, sender=UserProfileModel)
def delete_user_account(sender, **kwargs):
    """The receiver called after a user profile is deleted
    to delete its one_to_one relation"""

    kwargs['instance'].account.delete()


@receiver(pre_save, sender=UserAddressModel)
def add_sort_to_address(sender, **kwargs):
    """The receiver called before a user address is saved
    to give it a unique sort"""

    address = kwargs['instance']
    if not address.pk:
        latest_sort = UserAddressModel.objects.filter(user=address.user).count()
        address.sort = latest_sort + 1


@receiver(pre_save, sender=UserAddressModel)
def add_country_and_city(sender, **kwargs):
    """The receiver called before a user address is saved
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
    except Exception:
        pass


@receiver(post_delete, sender=UserAddressModel)
def resort_addresses(sender, **kwargs):
    """The receiver called after a user address is deleted
    to resort them"""

    address = kwargs['instance']
    address.user.addresses.filter(sort__gt=address.sort).update(sort=F('sort') - 1)
