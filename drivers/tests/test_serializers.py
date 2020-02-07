#  Copyright (c) Code Written and Tested by Ahmed Emad in 07/02/2020, 21:40
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from drivers.models import DriverProfileModel, DriverReviewModel
from drivers.serializers import DriverProfileSerializer, DriverReviewSerializer
from users.models import UserProfileModel


def create_image_file(name, content_type):
    path = '/media/drivers/sample.png'
    file_path = settings.BASE_DIR + path
    file_name = name
    content = open(file_path, 'rb').read()

    image_file = SimpleUploadedFile(name=file_name,
                                    content=content,
                                    content_type=content_type)

    return image_file


class TestDrivers(TestCase):
    """UnitTest for users serializers"""

    def test_vehicle_type(self):
        """test for driver vehicle type"""

        img_file = create_image_file('test_img.png', 'image/png')

        # true
        serializer = DriverProfileSerializer(data={'account': {'username': 'username',
                                                               'password': 'super_secret'},
                                                   'profile_photo': img_file, 'phone_number': 1234,
                                                   'vehicle_type': 'B', 'is_available': True,
                                                   'live_location_longitude': 30,
                                                   'live_location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # wrong type
        serializer = DriverProfileSerializer(data={'account': {'username': 'username',
                                                               'password': 'super_secret'},
                                                   'profile_photo': img_file, 'phone_number': 1234,
                                                   'vehicle_type': 'W', 'is_available': True,
                                                   'live_location_longitude': 30,
                                                   'live_location_latitude': 30})
        self.assertFalse(serializer.is_valid())

    def test_driver_location(self):
        """test for driver location"""

        img_file = create_image_file('test_img.png', 'image/png')

        # true
        serializer = DriverProfileSerializer(data={'account': {'username': 'username',
                                                               'password': 'super_secret'},
                                                   'profile_photo': img_file, 'phone_number': 1234,
                                                   'vehicle_type': 'B', 'is_available': True,
                                                   'live_location_longitude': 30,
                                                   'live_location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # wrong longitude
        serializer = DriverProfileSerializer(data={'account': {'username': 'username',
                                                               'password': 'super_secret'},
                                                   'profile_photo': img_file, 'phone_number': 1234,
                                                   'vehicle_type': 'B', 'is_available': True,
                                                   'live_location_longitude': 1000,
                                                   'live_location_latitude': 30})
        self.assertFalse(serializer.is_valid())

        # wrong latitude
        serializer = DriverProfileSerializer(data={'account': {'username': 'username',
                                                               'password': 'super_secret'},
                                                   'profile_photo': img_file, 'phone_number': 1234,
                                                   'vehicle_type': 'B', 'is_available': True,
                                                   'live_location_longitude': 30,
                                                   'live_location_latitude': -200})
        self.assertFalse(serializer.is_valid())

    def test_reviews_count(self):
        """test for driver number of reviews func"""

        account = User.objects.create_user(username='username', password='password')
        driver_profile = DriverProfileModel.objects.create(account=account, phone_number=12345,
                                                           vehicle_type='M', profile_photo='/media/drivers/sample.png')
        account2 = User.objects.create_user(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=account2, phone_number=12345)

        DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                         text='text', stars=5)

        serializer = DriverProfileSerializer(driver_profile)
        self.assertEqual(serializer.data.get('reviews_count', 0), 1)

        DriverReviewModel.objects.create(user=user_profile, driver=driver_profile,
                                         text='text', stars=5)

        serializer = DriverProfileSerializer(driver_profile)
        self.assertEqual(serializer.data.get('reviews_count', 0), 2)


class TestReviews(TestCase):
    """UnitTest for driver reviews serializers"""

    def test_review_stars(self):
        """test for driver reviews stars number"""

        # right
        serializer = DriverReviewSerializer(data={'stars': 3, 'text': 'text'})
        self.assertTrue(serializer.is_valid())

        # wrong has two decimal places
        serializer = DriverReviewSerializer(data={'stars': 3.55, 'text': 'text'})
        self.assertFalse(serializer.is_valid())

        # wrong has decimals indivisible by 5
        serializer = DriverReviewSerializer(data={'stars': 3.2, 'text': 'text'})
        self.assertFalse(serializer.is_valid())

        # wrong more than 5
        serializer = DriverReviewSerializer(data={'stars': 10, 'text': 'text'})
        self.assertFalse(serializer.is_valid())

        # wrong less than 0.5
        serializer = DriverReviewSerializer(data={'stars': 0, 'text': 'text'})
        self.assertFalse(serializer.is_valid())
