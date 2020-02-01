#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/02/2020, 00:34

from django.test import TestCase
from django.urls import reverse, resolve

from users.views import UserProfileView, user_login, UserAddressView


class TestUsers(TestCase):
    """Test for the users urls"""

    def test_signup(self):
        """test for signup url"""
        url = reverse('users:signup')
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'post': 'create'}).__name__)

    def test_login(self):
        """test for login url"""
        url = reverse('users:login')
        self.assertEqual(resolve(url).func, user_login)

    def test_user_details(self):
        """test for user details url"""
        url = reverse('users:details', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'get': 'retrieve'}).__name__)


class TestAdresses(TestCase):
    """Test for the users addresses urls"""

    def test_addresses_list(self):
        """test for users addresseses list url"""
        url = reverse('users:addresses-list', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         UserAddressView.as_view({'get': 'list'}).__name__)

    def test_addresses_detail(self):
        """test for users addresses details url"""
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         UserAddressView.as_view({'get': 'retrieve'}).__name__)
