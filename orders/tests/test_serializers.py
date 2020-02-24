#  Copyright (c) Code Written and Tested by Ahmed Emad in 24/02/2020, 12:36
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from drivers.models import DriverProfileModel
from orders.models import OrderModel
from orders.serializers import OrderDetailSerializer
from shops.models import ShopProfileModel, ProductModel, ShopAddressModel


class TestOrder(TestCase):
    """Unittest for order serializer"""

    def setUp(self):
        """setup for unittest"""
        shop_user = User.objects.create(username='shop_user', password='password')
        self.shop = ShopProfileModel.objects.create(account=shop_user, profile_photo='/orders/tests/sample.jpg',
                                                    cover_photo='/orders/tests/sample.jpg', phone_number=123,
                                                    description='text', shop_type='F', name='shop',
                                                    slug='shop', currency='$', delivery_fee=0,
                                                    opens_at=timezone.now() - timezone.timedelta(hours=2),
                                                    closes_at=timezone.now() + timezone.timedelta(hours=2),
                                                    time_to_prepare=20, vat=14, is_active=True)
        self.shop_address = ShopAddressModel.objects.create(shop=self.shop, area='area',
                                                            street='street', building='building',
                                                            location_longitude=30,
                                                            location_latitude=30)
        self.product = ProductModel.objects.create(shop=self.shop, photo='/orders/tests/sample.jpg',
                                                   title='product', slug='product', price=5,
                                                   description='text')

        driver_user = User.objects.create(username='driver_user', password='password')
        self.driver = DriverProfileModel.objects.create(account=driver_user, phone_number=123,
                                                        profile_photo='/orders/tests/sample.jpg',
                                                        is_active=True, is_available=True,
                                                        last_time_online=timezone.now(),
                                                        live_location_longitude=30,
                                                        live_location_latitude=30)

    def test_driver_available(self):
        """test if there are any drivers available or not"""

        # true
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})

        self.assertTrue(serializer.is_valid())

        # no driver in this range
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 12,
                                                                      'location_latitude': 43}})

        self.assertFalse(serializer.is_valid())

    def test_shops_nearby(self):
        """test whether all shop are near the shipping address"""

        # true
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertTrue(serializer.is_valid())

        # far away from the product's shop
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 12,
                                                                      'location_latitude': 46}})
        self.assertFalse(serializer.is_valid())

    def test_order_status(self):
        """test for order status post validate"""

        order = OrderModel.objects.create(final_price=0, subtotal=0, delivery_fee=0, vat=0)
        # true
        serializer = OrderDetailSerializer(data={'status': 'P'}, instance=order, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        # wrong status
        serializer = OrderDetailSerializer(data={'status': 'wrong'}, instance=order, partial=True)
        self.assertFalse(serializer.is_valid())

        # can't reverse the status back
        serializer = OrderDetailSerializer(data={'status': 'C'}, instance=order, partial=True)
        self.assertFalse(serializer.is_valid())
