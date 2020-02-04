#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/02/2020, 18:40
from django.contrib.auth.models import User
from django.test import TestCase

from users.serializers import UserSerializer, UserAddressSerializer


class TestUsers(TestCase):
    """UnitTest for users serializers"""

    def test_username_unique(self):
        """test for username uniqueness"""

        User.objects.create(username='username', password='password')
        serializer = UserSerializer(data={'username': 'username', 'password': 'super_secret'})
        self.assertFalse(serializer.is_valid())

    def test_password_validation(self):
        """test for password validation"""

        # true
        serializer = UserSerializer(data={'username': 'username', 'password': 'super_secret'})
        self.assertTrue(serializer.is_valid())

        # less than 8 chars
        serializer = UserSerializer(data={'username': 'username', 'password': 'hi'})
        self.assertFalse(serializer.is_valid())

        # user attr similar
        serializer = UserSerializer(data={'username': 'username', 'password': 'username'})
        self.assertFalse(serializer.is_valid())

        # common password
        serializer = UserSerializer(data={'username': 'username', 'password': 'password'})
        self.assertFalse(serializer.is_valid())

        # numbers only
        serializer = UserSerializer(data={'username': 'username', 'password': '123456789'})
        self.assertFalse(serializer.is_valid())


class TestAddresses(TestCase):
    """UnitTest for users serializers"""

    def test_address_type(self):
        """test for address type choices"""

        # right
        serializer = UserAddressSerializer(data={'title': 'title', 'area': 'area', 'type': 'A',
                                                 'street': 'street', 'building': 'building',
                                                 'location_longitude': 30, 'location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # wrong
        serializer = UserAddressSerializer(data={'title': 'title', 'area': 'area', 'type': 'S',  # wrong
                                                 'street': 'street', 'building': 'building',
                                                 'location_longitude': 30, 'location_latitude': 30})
        self.assertFalse(serializer.is_valid())

    def test_address_location(self):
        """test for address location"""

        # true
        serializer = UserAddressSerializer(data={'title': 'title', 'area': 'area', 'type': 'A',
                                                 'street': 'street', 'building': 'building',
                                                 'location_longitude': 30, 'location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # wrong longitude
        serializer = UserAddressSerializer(data={'title': 'title', 'area': 'area', 'type': 'A',
                                                 'street': 'street', 'building': 'building',
                                                 'location_longitude': 1000, 'location_latitude': 30})
        self.assertFalse(serializer.is_valid())

        # wrong latitude
        serializer = UserAddressSerializer(data={'title': 'title', 'area': 'area', 'type': 'A',
                                                 'street': 'street', 'building': 'building',
                                                 'location_longitude': 30, 'location_latitude': -200})
        self.assertFalse(serializer.is_valid())
