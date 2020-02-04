#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 00:39
from django.contrib.auth.models import User
from django.test import TestCase

from users.models import photo_upload, UserAddressModel, UserProfileModel


class TestUsers(TestCase):
    """UnitTest for users models"""

    def test_photo_name_unique(self):
        """test for image upload unique id generator"""

        image_1_id = photo_upload(None, 'image1')
        image_2_id = photo_upload(None, 'image2')
        self.assertNotEquals(image_1_id, image_2_id)

    def test_user_str(self):
        """test for user __str__ unction"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        self.assertEqual(user_profile.__str__(), user.username)


class TestAddresses(TestCase):
    """UnitTest for addresses models"""

    def test_address_sort_unique(self):
        """test for address sort uniqueness"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)

        address1 = UserAddressModel.objects.create(user=user_profile, title='title', area='area',
                                                   type='A', street='street', building='building',
                                                   location_longitude=0, location_latitude=0)
        self.assertEqual(address1.sort, 1)

        address2 = UserAddressModel.objects.create(user=user_profile, title='title', area='area',
                                                   type='A', street='street', building='building',
                                                   location_longitude=0, location_latitude=0)
        self.assertEqual(address2.sort, 2)
        self.assertNotEquals(address1.sort, address2.sort)

        address1.delete()
        address2.refresh_from_db()
        self.assertEqual(address2.sort, 1)  # resorted from signals

    def test_address_str(self):
        """test for adress __str__ unction"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        address = UserAddressModel.objects.create(user=user_profile, title='title', area='area',
                                                  type='A', street='street', building='building',
                                                  location_longitude=0, location_latitude=0)
        self.assertEqual(address.__str__(), address.title)
