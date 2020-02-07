#  Copyright (c) Code Written and Tested by Ahmed Emad in 07/02/2020, 23:11
from django.contrib.auth.models import User
from django.test import TestCase

from drivers.models import photo_upload, DriverReviewModel, DriverProfileModel
from users.models import UserProfileModel


class TestDrivers(TestCase):
    """UnitTest for drivers model"""

    def test_photo_name_unique(self):
        """test for image upload unique id generator"""

        image_1_id = photo_upload(None, 'image1')
        image_2_id = photo_upload(None, 'image2')
        self.assertNotEquals(image_1_id, image_2_id)

    def test_driver_str(self):
        """test for driver __str__ unction"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/drivers/tests/sample.jpg')
        self.assertEqual(driver_profile.__str__(), account.username)

    def test_driver_account_delete(self):
        """test for account delete after profile deletion from signals"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/drivers/tests/sample.jpg')
        driver_profile.delete()
        self.assertEqual(User.objects.filter(username='username').exists(), False)


class TestAddresses(TestCase):
    """UnitTest for reviews model"""

    def test_review_sort_unique(self):
        """test for review sort uniqueness"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/drivers/tests/sample.jpg')

        account2 = User.objects.create_user(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=account2, phone_number=12345)

        review = DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                                  text='text', stars=5)
        self.assertEqual(review.sort, 1)

        review2 = DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                                   text='text', stars=5)
        self.assertEqual(review2.sort, 2)
        self.assertNotEquals(review.sort, review2.sort)

        review.delete()
        review2.refresh_from_db()
        self.assertEqual(review2.sort, 1)  # resorted from signals

    def test_review_str(self):
        """test for review __str__ unction"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/drivers/tests/sample.jpg')

        account2 = User.objects.create_user(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=account2, phone_number=12345)

        review = DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                                  text='text', stars=5)
        self.assertEqual(review.__str__(), review.text)

    def test_driver_rating(self):
        """test for calculate driver rating from reviews func"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/drivers/tests/sample.jpg')

        account2 = User.objects.create_user(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=account2, phone_number=12345)

        review = DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                                  text='text', stars=5)
        driver_profile.refresh_from_db()
        self.assertEqual(driver_profile.rating, review.stars)

        review2 = DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                                   text='text', stars=4)
        driver_profile.refresh_from_db()
        self.assertEqual(driver_profile.rating, (review.stars + review2.stars) / 2)  # averge of reviews
