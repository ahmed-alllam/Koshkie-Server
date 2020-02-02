#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/02/2020, 23:44

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from users.models import UserProfileModel, UserAddressModel


class TestUsers(TestCase):
    """Unit Test for users app's views"""

    def test_login(self):
        """Test for users login view"""

        user = User.objects.create_user(username='username', password='password')
        url = reverse('users:login')

        # wrong login password
        response = self.client.post(url, {'username': 'username',
                                          'password': 'a wrong password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # user has no profile not valid
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right login
        UserProfileModel.objects.create(account=user, phone_number=12345)
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # user already logged in
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
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
        """Test for users signup view"""
        url = reverse('users:signup')

        # right sign up
        response = self.client.post(url, {'account': {
            'first_name': 'my first name',
            'last_name': 'my last name',
            'username': 'username',
            'password': 'super_secret'
        },
            'phone_number': 12345},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # already logged in
        response = self.client.post(url, {'account': {
            'username': 'username',
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        },
            'phone_number': 12345},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

        # creating user with a taken username
        self.client.logout()
        response = self.client.post(url, {'account': {
            'username': 'username',  # taken
            'password': 'super_secret',
            'first_name': 'my first name',
            'last_name': 'my last name'
        },
            'phone_number': 12345},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # creating user with a non valid password
        response = self.client.post(url, {'account': {
            'username': 'no_taken_username',
            'password': '123',
            'first_name': 'my first name',
            'last_name': 'my last name'
        },
            'phone_number': 12345},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        """Test for users get view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user, phone_number=12345)
        url = reverse('users:details', kwargs={'username': 'username'})

        # right
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong user
        url = reverse('users:details', kwargs={'username': 'non existing username'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        """Test for users update view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user, phone_number=12345)
        url = reverse('users:details', kwargs={'username': 'username'})

        # not logged in as that user
        reponse = self.client.put(url, {'account': {
            'username': 'username',
            'password': '123',
            'first_name': 'my first name',
            'last_name': 'my last name'
        },
            'phone_number': 12345},
                                  content_type='application/json')
        self.assertEqual(reponse.status_code, 403)

        # wrong or uncomplete data
        self.client.force_login(user)
        reponse = self.client.put(url, {'account': {'first_name': 'my first name'}},
                                  content_type='application/json')
        self.assertEqual(reponse.status_code, 400)

        # un complete data passes the patch request
        reponse = self.client.patch(url, {'account': {'first_name': 'my first name'}},
                                    content_type='application/json')
        self.assertEqual(reponse.status_code, 200)

        # wrong username
        url = reverse('users:details', kwargs={'username': 'non existing username'})
        reponse = self.client.put(url, {'account': {
            'username': 'username',
            'password': '123',
            'first_name': 'my first name',
            'last_name': 'my last name'
        },
            'phone_number': 12345},
                                  content_type='application/json')
        self.assertEqual(reponse.status_code, 404)

    def test_delete_user(self):
        """Test for users delete view"""

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user, phone_number=12345)
        url = reverse('users:details', kwargs={'username': 'username'})

        # is not logged in as that user
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # wrong username
        self.client.force_login(user)
        url = reverse('users:details', kwargs={'username': 'non existing username'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # right
        url = reverse('users:details', kwargs={'username': 'username'})
        self.client.force_login(user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.filter(username='username').exists(), False)


class TestAddresses(TestCase):
    """Unit Test for users addresses views"""

    def test_list_addresses(self):

        """Test for users address list view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        UserAddressModel.objects.create(user=user_profile, title='title', area='area', type='A',
                                        street='street', building='building', location_longitude=0,
                                        location_latitude=0)
        url = reverse('users:addresses-list', kwargs={'username': 'username'})

        # not logged
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('users:addresses-list', kwargs={'username': 'non existing username'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_address(self):
        """Test for users address get view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        UserAddressModel.objects.create(user=user_profile, title='title', area='area', type='A',
                                        street='street', building='building', location_longitude=0,
                                        location_latitude=0)
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 1})

        # not logged
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('users:addresses-detail', kwargs={'username': 'non existing username',
                                                        'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # wrong address pk
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 123})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_address(self):
        """Test for users address create view"""
        # todo
        pass

    def test_update_address(self):
        """Test for users address update view"""
        # todo
        pass

    def test_delete_address(self):
        """Test for users address delete view"""
        # todo
        pass
