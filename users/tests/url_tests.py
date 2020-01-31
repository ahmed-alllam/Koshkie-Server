#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

from django.test import TestCase
from django.urls import reverse, resolve

from users.views import UserProfileView, user_login, UserAddressView


class TestUrls(TestCase):
    """Test for the users app urls"""

    def test_signup(self):
        """test for signup url view"""
        url = reverse('users:signup')
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'post': 'create'}).__name__)

    def test_login(self):
        """test for login url view"""
        url = reverse('users:login')
        self.assertEqual(resolve(url).func, user_login)

    def test_user_details(self):
        """test for user details url view"""
        url = reverse('users:details', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         UserProfileView.as_view({'get': 'retrieve'}).__name__)

    def test_addresses_list(self):
        """test for user addresses list url view"""
        url = reverse('users:addresses-list', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         UserAddressView.as_view({'get': 'list'}).__name__)

    def test_addresses_detail(self):
        """test for user address details url view"""
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         UserAddressView.as_view({'get': 'retrieve'}).__name__)
