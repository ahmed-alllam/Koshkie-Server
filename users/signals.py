#  Copyright (c) Code Written and Tested by Ahmed Emad in 24/01/2020, 15:41
from django.db.models import F
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from users.models import UserProfileModel, UserAddressModel


@receiver(post_delete, sender=UserProfileModel)
def delete_user_account(sender, **kwargs):
    """The receiver called after a user profile is deleted """
    kwargs['instance'].account.delete()


@receiver(pre_save, sender=UserAddressModel)
def resort_addresses(sender, **kwargs):
    """The receiver called before a user address is saved"""
    address = kwargs['instance']
    if not address.pk:
        latest_sort = UserAddressModel.objects.filter(user=address.user).count()
        address.sort = latest_sort + 1


@receiver(post_delete, sender=UserAddressModel)
def resort_addresses(sender, **kwargs):
    """The receiver called after a user address is deleted """
    address = kwargs['instance']
    address.user.addresses.filter(sort__gt=address.sort).update(sort=F('sort') - 1)
