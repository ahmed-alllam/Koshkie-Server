#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/02/2020, 00:34
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from users.models import UserProfileModel


class TestUsers(TestCase):
    """Unit Test for users app's views"""

    def test_login(self):
        """Test for users login view"""

        user = User.objects.create_user(username='username', password='password')
        url = reverse('users:login')

        # wrong login password
        response = self.client.post(url, {'username': 'username',
                                          'password': 'a wrong password'})
        self.assertEqual(response.status_code, 400)

        # user has no profile
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'})
        self.assertEqual(response.status_code, 400)

        # right login
        UserProfileModel.objects.create(account=user, phone_number=12345)
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'})
        self.assertEqual(response.status_code, 200)

        # user already logged in
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'})
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Test for users logout view"""

        user = User.objects.create_user(username='username', password='password')

        # user is logged in
        url = reverse('logout')
        self.client.force_login(user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        # user is NOT logged in
        response = self.client.post(url)
        self.assertEqual(response.status_code, 401)

    def test_signup(self):
        pass
