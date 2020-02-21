#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 17:27
from django.test import TestCase
from django.urls import reverse, resolve

from orders.views import OrderView


class OrdersTest(TestCase):
    """UnitTest for orders urls"""

    def test_orders_list(self):
        """test for orders list url"""
        url = reverse('orders:orders-list')
        self.assertEqual(resolve(url).func.__name__,
                         OrderView.as_view({'get': 'list'}).__name__)

    def test_orders_detail(self):
        """test for orders detail url"""
        url = reverse('orders:orders-detail', kwargs={'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         OrderView.as_view({'get': 'retrieve'}).__name__)
