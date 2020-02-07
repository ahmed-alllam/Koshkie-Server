#  Copyright (c) Code Written and Tested by Ahmed Emad in 07/02/2020, 21:40
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, client
from django.urls import reverse

from drivers.models import DriverProfileModel
from users.models import UserProfileModel, UserAddressModel


def img_file():
    path = '/media/drivers/sample.png'
    file_path = settings.BASE_DIR + path
    file_name = 'test_img.png'
    content = open(file_path, 'rb').read()

    image_file = SimpleUploadedFile(name=file_name,
                                    content=content,
                                    content_type='image/png')

    return image_file


class TestDrivers(TestCase):
    """Unit Test for drivers app's views"""

    def test_login(self):
        """Test for drivers login view"""

        account = User.objects.create_user(username='username', password='password')
        url = reverse('drivers:login')

        # user has no profile not valid
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        UserProfileModel.objects.create(account=account, phone_number=12345)

        # user has a user profile not a driver profile
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        DriverProfileModel.objects.create(account=account, phone_number=12345,
                                          profile_photo='/media/drivers/sample.png')

        # wrong login password
        response = self.client.post(url, {'username': 'username',
                                          'password': 'a wrong password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right login
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # user already logged in
        response = self.client.post(url, {'username': 'username',
                                          'password': 'password'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_signup(self):
        """Test for drivers signup view"""
        url = reverse('drivers:signup')

        # right sign up
        response = self.client.post(url, {  # using multipart-form_data
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        self.assertEqual(response.status_code, 201)

        # already logged in
        response = self.client.post(url, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        self.assertEqual(response.status_code, 401)

        # creating driver with a taken username
        self.client.logout()
        response = self.client.post(url, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'username',  # taken
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        self.assertEqual(response.status_code, 400)

        # creating driver with a non valid password
        response = self.client.post(url, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'not_taken_username',
            'account.password': '123',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        self.assertEqual(response.status_code, 400)

    def test_get_driver(self):
        """Test for drivers get view"""

        user = User.objects.create_user(username='username', password='password')
        DriverProfileModel.objects.create(account=user, phone_number=12345,
                                          profile_photo='/media/drivers/sample.png')
        url = reverse('drivers:details', kwargs={'username': 'username'})

        # right
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('drivers:details', kwargs={'username': 'non existing username'})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_update_driver(self):
        """Test for drivers update view"""

        user = User.objects.create_user(username='username', password='password')
        DriverProfileModel.objects.create(account=user, phone_number=12345)
        url = reverse('drivers:details', kwargs={'username': 'username'})

        # not logged in as that driver
        post_data = client.encode_multipart(client.BOUNDARY, {  # using multipart-form_data
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'the_new_username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})

        reponse = self.client.put(url, post_data,
                                  content_type=client.MULTIPART_CONTENT)
        self.assertEqual(reponse.status_code, 403)

        # not logged in as that driver
        user2 = User.objects.create_user(username='username2', password='password')
        DriverProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        post_data = client.encode_multipart(client.BOUNDARY, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'the_new_username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        reponse = self.client.put(url, post_data,
                                  content_type=client.MULTIPART_CONTENT)
        self.assertEqual(reponse.status_code, 403)

        # wrong or uncomplete data
        self.client.force_login(user)
        reponse = self.client.put(url, {'account': {'first_name': 'my first name2'}},
                                  content_type='application/json')  # has only json no files
        self.assertEqual(reponse.status_code, 400)

        # uncomplete data passes the patch request right
        reponse = self.client.patch(url, {'account': {'first_name': 'my first name2'}},
                                    content_type='application/json')  # has only json no files
        self.assertEqual(reponse.status_code, 200)

        # right
        post_data = client.encode_multipart(client.BOUNDARY, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'the_new_username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        reponse = self.client.put(url, post_data,
                                  content_type=client.MULTIPART_CONTENT)
        self.assertEqual(reponse.status_code, 200)

        # wrong username
        url = reverse('drivers:details', kwargs={'username': 'non existing username'})
        post_data = client.encode_multipart(client.BOUNDARY, {
            'account.first_name': 'my first name',
            'account.last_name': 'my last name',
            'account.username': 'the_new_username',
            'account.password': 'super_secret',
            'phone_number': 12345, 'vehicle_type': 'B', 'profile_photo': img_file()})
        reponse = self.client.put(url, post_data,
                                  content_type=client.MULTIPART_CONTENT)
        self.assertEqual(reponse.status_code, 404)

    def test_delete_driver(self):
        """Test for drivers delete view"""

        account = User.objects.create_user(username='username', password='password')
        DriverProfileModel.objects.create(account=account, phone_number=12345,
                                          profile_photo=img_file())
        url = reverse('drivers:details', kwargs={'username': 'username'})

        # is not logged in as that driver
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # is not logged in as that driver
        account2 = User.objects.create_user(username='username2', password='password')
        DriverProfileModel.objects.create(account=account2, phone_number=12345,
                                          profile_photo=img_file())
        self.client.force_login(account2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # wrong username
        self.client.force_login(account)
        url = reverse('drivers:details', kwargs={'username': 'non existing username'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # right
        url = reverse('drivers:details', kwargs={'username': 'username'})
        self.client.force_login(account)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.filter(username='username').exists(), False)


class TestReviews(TestCase):
    """Unit Test for drivers reviews views"""

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

        user = User.objects.create_user(username='username', password='password')
        UserProfileModel.objects.create(account=user, phone_number=12345)
        url = reverse('users:addresses-list', kwargs={'username': 'username'})

        # not logged
        response = self.client.post(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                          'street': 'street', 'building': 'building',
                                          'location_longitude': 0, 'location_latitude': 0},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        response = self.client.post(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                          'street': 'street', 'building': 'building',
                                          'location_longitude': 0, 'location_latitude': 0},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.post(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                          'street': 'street', 'building': 'building',
                                          'location_longitude': 0, 'location_latitude': 0},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['sort'], 1)  # check for sort from signals

        # wrong data
        response = self.client.post(url, {'title': 'title', 'area': 'area', 'type': 'wrong type',
                                          'street': 'street', 'building': 'building'},  # missing attrs
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # wrong username
        url = reverse('users:addresses-list', kwargs={'username': 'non existing username'})
        response = self.client.post(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                          'street': 'street', 'building': 'building',
                                          'location_longitude': 0, 'location_latitude': 0},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_address(self):
        """Test for users address update view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        UserAddressModel.objects.create(user=user_profile, title='title', area='area', type='A',
                                        street='street', building='building', location_longitude=0,
                                        location_latitude=0)
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 1})

        # not logged
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                         'street': 'street', 'building': 'building',
                                         'location_longitude': 0, 'location_latitude': 0},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                         'street': 'street', 'building': 'building',
                                         'location_longitude': 0, 'location_latitude': 0},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                         'street': 'street', 'building': 'building',
                                         'location_longitude': 0, 'location_latitude': 0},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data for put
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'wrong type',
                                         'street': 'street', 'building': 'building'},  # missing attrs
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # right for patch
        response = self.client.patch(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                           'street': 'street', 'building': 'building'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong username
        url = reverse('users:addresses-detail', kwargs={'username': 'non existing username', 'pk': 1})
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                         'street': 'street', 'building': 'building',
                                         'location_longitude': 0, 'location_latitude': 0},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # wrong address pk
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 123})
        response = self.client.put(url, {'title': 'title', 'area': 'area', 'type': 'A',
                                         'street': 'street', 'building': 'building',
                                         'location_longitude': 0, 'location_latitude': 0},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_address(self):
        """Test for users address delete view"""

        user = User.objects.create_user(username='username', password='password')
        user_profile = UserProfileModel.objects.create(account=user, phone_number=12345)
        UserAddressModel.objects.create(user=user_profile, title='title', area='area', type='A',
                                        street='street', building='building', location_longitude=0,
                                        location_latitude=0)
        address2 = UserAddressModel.objects.create(user=user_profile, title='title', area='area', type='A',
                                                   street='street', building='building', location_longitude=0,
                                                   location_latitude=0)
        self.assertEqual(address2.sort, 2)
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 1})

        # not logged
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # not logged in as that user
        user2 = User.objects.create_user(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=12345)
        self.client.force_login(user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

        # right
        self.client.force_login(user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        address2.refresh_from_db()
        self.assertEqual(address2.sort, 1)  # resorted from signals

        # wrong username
        url = reverse('users:addresses-detail', kwargs={'username': 'non existing username', 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

        # wrong address pk
        url = reverse('users:addresses-detail', kwargs={'username': 'username', 'pk': 123})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
