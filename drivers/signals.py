#  Copyright (c) Code Written and Tested by Ahmed Emad in 06/02/2020, 16:49
from django.db.models import F
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

from drivers.models import DriverProfileModel, DriverReviewModel


@receiver(post_delete, sender=DriverProfileModel)
def delete_driver_account(sender, **kwargs):
    """The receiver called after a driver profile is deleted
    to delete its one_to_one relation"""

    kwargs['instance'].account.delete()


@receiver(pre_save, sender=DriverReviewModel)
def add_sort_to_review(sender, **kwargs):
    """The receiver called before a driver review is saved
    to give it a unique sort"""

    review = kwargs['instance']
    if not review.pk:
        latest_sort = DriverReviewModel.objects.filter(driver=review.driver).count()
        review.sort = latest_sort + 1


@receiver(post_save, sender=DriverReviewModel)
def add_new_rating_driver(sender, **kwargs):
    """The receiver called after a driver review is saved
    to give the driver a new rating"""

    review = kwargs['instance']
    review.driver.calculate_rating()
    review.driver.save()


@receiver(post_delete, sender=DriverReviewModel)
def resort_reviews(sender, **kwargs):
    """The receiver called after a driver review is deleted
    to resort them and give the driver a new rating"""

    review = kwargs['instance']
    review.driver.reviews.filter(sort__gt=review.sort).update(sort=F('sort') - 1)
    review.driver.calculate_rating()
    review.driver.save()
