#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 17:27
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from drivers.models import DriverProfileModel
from orders.models import OrderModel
from shops.models import ShopProfileModel, ProductModel, ShopAddressModel
from users.models import UserProfileModel


class TestOrders(TestCase):
    """Unittest for orders views"""

    def setUp(self):
        """set up for unit test"""
        user = User.objects.create(username='usernameshop', password='password')
        shop = ShopProfileModel.objects.create(account=user, profile_photo='/orders/tests/sample.jpg',
                                               cover_photo='/orders/tests/sample.jpg', phone_number=123,
                                               description='text', shop_type='F', name='shop',
                                               slug='shop', currency='$', delivery_fee=0,
                                               opens_at=timezone.now() - timezone.timedelta(hours=2),
                                               closes_at=timezone.now() + timezone.timedelta(hours=2),
                                               time_to_prepare=20, vat=14,
                                               is_active=True)
        ShopAddressModel.objects.create(shop=shop, area='area', street='street', building='b',
                                        location_longitude=30, location_latitude=30)
        self.product = ProductModel.objects.create(shop=shop, photo='/orders/tests/sample.jpg',
                                                   title='product', slug='product', price=5,
                                                   description='text')
        DriverProfileModel.objects.create(account=user, phone_number=123,
                                          profile_photo='/orders/tests/sample.jpg',
                                          is_active=True, is_available=True,
                                          last_time_online=timezone.now(),
                                          live_location_longitude=30,
                                          live_location_latitude=30)

    def test_list_orders(self):
        """test for orders list view"""
        url = reverse('orders:orders-list')

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # has no profile
        user = User.objects.create(username='username', password='password')
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # has a valid profile - right but has no orders yet
        user2 = User.objects.create(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=user2, phone_number=123)
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 0)

        # right and has an order
        order = OrderModel.objects.create(user=user_profile, final_price=0, subtotal=0,
                                          delivery_fee=0, vat=0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 1)

        # try the same with driver
        user3 = User.objects.create(username='username3', password='password')
        driver = DriverProfileModel.objects.create(account=user3, phone_number=123,
                                                   profile_photo='/orders/tests/sample.jpg')
        self.client.force_login(user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 0)

        order.driver = driver
        order.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 1)

        # try the same with shop
        user4 = User.objects.create(username='username4', password='password')
        shop = ShopProfileModel.objects.create(account=user4, phone_number=123,
                                               profile_photo='/orders/tests/sample.jpg',
                                               cover_photo='/orders/tests/sample.jpg',
                                               description='text', shop_type='F', name='shop',
                                               slug='shop', currency='$', delivery_fee=0,
                                               opens_at=timezone.now() - timezone.timedelta(hours=2),
                                               closes_at=timezone.now() + timezone.timedelta(hours=2),
                                               time_to_prepare=20, vat=14)
        self.client.force_login(user4)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 0)

        order.shops.add(shop)
        order.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)['orders']), 1)

    def test_get_order(self):
        """test for orders get view"""
        url = reverse('orders:orders-detail', kwargs={'pk': 3})

        # not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # has no profile
        user = User.objects.create(username='username', password='password')
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # has a valid profile - right but it order no saved yes 404
        user2 = User.objects.create(username='username2', password='password')
        user_profile = UserProfileModel.objects.create(account=user2, phone_number=123)
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # right and has an order
        order = OrderModel.objects.create(user=user_profile, final_price=0,
                                          subtotal=0, delivery_fee=0, vat=0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # try the same but with another user that is
        # not the owner of the order
        user3 = User.objects.create(username='username3', password='password')
        UserProfileModel.objects.create(account=user3, phone_number=123)
        self.client.force_login(user3)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # try the same but with driver
        user4 = User.objects.create(username='username4', password='password')
        driver = DriverProfileModel.objects.create(account=user4, phone_number=123,
                                                   profile_photo='/orders/tests/sample.jpg')
        self.client.force_login(user4)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        order.driver = driver
        order.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # try the same but with shop
        user5 = User.objects.create(username='username5', password='password')
        shop = ShopProfileModel.objects.create(account=user5, phone_number=123,
                                               profile_photo='/orders/tests/sample.jpg',
                                               cover_photo='/orders/tests/sample.jpg',
                                               description='text', shop_type='F', name='shop',
                                               slug='shop', currency='$', delivery_fee=0,
                                               opens_at=timezone.now() - timezone.timedelta(hours=2),
                                               closes_at=timezone.now() + timezone.timedelta(hours=2),
                                               time_to_prepare=20, vat=14)
        self.client.force_login(user5)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        order.shops.add(shop)
        order.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # try non existing pk
        url = reverse('orders:orders-detail', kwargs={'pk': 1234})
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_create_order(self):
        """test for orders create view"""
        url = reverse('orders:orders-list')

        # not logged in
        response = self.client.post(url, {'shipping_address': {'area': 'area', 'type': 'A',
                                                               'street': 'street', 'building': 'b',
                                                               'location_longitude': 30,
                                                               'location_latitude': 30},
                                          'items': [{'product': self.product.pk}]},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # has no user profile
        user = User.objects.create(username='username', password='password')
        self.client.force_login(user)
        response = self.client.post(url, {'shipping_address': {'area': 'area', 'type': 'A',
                                                               'street': 'street', 'building': 'b',
                                                               'location_longitude': 30,
                                                               'location_latitude': 30},
                                          'items': [{'product': self.product.pk}]},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # has driver profile not regular user profile
        user2 = User.objects.create(username='username2', password='password')
        DriverProfileModel.objects.create(account=user2, phone_number=123,
                                          profile_photo='/orders/tests/sample.jpg')
        self.client.force_login(user2)
        response = self.client.post(url, {'shipping_address': {'area': 'area', 'type': 'A',
                                                               'street': 'street', 'building': 'b',
                                                               'location_longitude': 30,
                                                               'location_latitude': 30},
                                          'items': [{'product': self.product.pk}]},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        user3 = User.objects.create(username='username3', password='password')
        UserProfileModel.objects.create(account=user3, phone_number=123)
        self.client.force_login(user3)
        response = self.client.post(url, {'shipping_address': {'area': 'area', 'type': 'A',
                                                               'street': 'street', 'building': 'b',
                                                               'location_longitude': 30,
                                                               'location_latitude': 30},
                                          'items': [{'product': self.product.pk}]},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # wrong data
        response = self.client.post(url, {'shipping_address': {'area': 'area', 'type': 'A',
                                                               'street': 'street', 'building': 'b',
                                                               'location_longitude': 30,
                                                               'location_latitude': 30},
                                          'items': [{'product': 1221}]},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_update_order(self):
        """test for orders update view"""

        order = OrderModel.objects.create(final_price=0, subtotal=0, delivery_fee=0, vat=0)

        url = reverse('orders:orders-detail', kwargs={'pk': order.pk})

        # not looged in
        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # has no profile
        user = User.objects.create(username='username', password='password')
        self.client.force_login(user)
        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # has user profile not driver profile
        user2 = User.objects.create(username='username2', password='password')
        UserProfileModel.objects.create(account=user2, phone_number=123)
        self.client.force_login(user2)
        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # right
        user3 = User.objects.create(username='username3', password='password')
        driver = DriverProfileModel.objects.create(account=user3, phone_number=123,
                                                   profile_photo='/orders/tests/sample.jpg')
        order.driver = driver
        order.save()
        self.client.force_login(user3)
        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # wrong data
        response = self.client.patch(url, {'status': 'wrong'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # not the driver of that order
        user4 = User.objects.create(username='username4', password='password')
        DriverProfileModel.objects.create(account=user4, phone_number=123,
                                          profile_photo='/orders/tests/sample.jpg')
        self.client.force_login(user4)
        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 403)

        # wrong pk in url
        url = reverse('orders:orders-detail', kwargs={'pk': 123})

        response = self.client.patch(url, {'status': 'P'},
                                     content_type='application/json')
        self.assertEqual(response.status_code, 404)
