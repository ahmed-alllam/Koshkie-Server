#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 21:06

from django.test import TestCase
from django.urls import reverse, resolve

from drivers.views import DriverProfileView, driver_login, DriverReviewView


class TestDrivers(TestCase):
    """Test for the drivers urls"""

    def test_signup(self):
        """test for signup url"""
        url = reverse('drivers:signup')
        self.assertEqual(resolve(url).func.__name__,
                         DriverProfileView.as_view({'post': 'create'}).__name__)

    def test_login(self):
        """test for login url"""
        url = reverse('drivers:login')
        self.assertEqual(resolve(url).func, driver_login)

    def test_driver_list(self):
        """test fro drivers list url"""
        url = reverse('drivers:list')
        self.assertEqual(resolve(url).func.__name__,
                         DriverProfileView.as_view({'get': 'list'}).__name__)

    def test_driver_details(self):
        """test for driver details url"""
        url = reverse('drivers:details', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         DriverProfileView.as_view({'get': 'retrieve'}).__name__)


class TestDriverReviews(TestCase):
    """Test for the drivers reviews urls"""

    def test_reviews_list(self):
        """test for drivers reviews list url"""
        url = reverse('drivers:reviews-list', kwargs={'username': 'username'})
        self.assertEqual(resolve(url).func.__name__,
                         DriverReviewView.as_view({'get': 'list'}).__name__)

    def test_reviews_detail(self):
        """test for drivers reviews details url"""
        url = reverse('drivers:reviews-detail', kwargs={'username': 'username', 'pk': 1})
        self.assertEqual(resolve(url).func.__name__,
                         DriverReviewView.as_view({'get': 'retrieve'}).__name__)
