#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/02/2020, 17:27
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from orders.models import OrderItemModel, Choice, OrderItemsGroupModel, OrderModel
from shops.models import ShopProfileModel, ProductModel, AddOnModel, OptionGroupModel, OptionModel


class TestOrderItemsGroup(TestCase):
    """Unittest for order items group model"""

    def setUp(self):
        """setup for tests"""
        user = User.objects.create(username='username', password='password')
        self.shop = ShopProfileModel.objects.create(account=user, profile_photo='/orders/tests/sample.jpg',
                                                    cover_photo='/orders/tests/sample.jpg', phone_number=123,
                                                    description='text', shop_type='F', name='shop',
                                                    slug='shop', currency='$', delivery_fee=0,
                                                    opens_at=timezone.now() - timezone.timedelta(hours=2),
                                                    closes_at=timezone.now() + timezone.timedelta(hours=2),
                                                    time_to_prepare=20, vat=14)
        self.order = OrderModel.objects.create(final_price=0, subtotal=0, delivery_fee=0, vat=0)

    def test_str(self):
        """test for string function"""
        group = OrderItemsGroupModel.objects.create(order=self.order, shop=self.shop)
        self.assertEqual(group.__str__(), '1: shop')

        group = OrderItemsGroupModel.objects.create()
        self.assertNotEqual(group.__str__(), '1: shop')


class TestOrderItem(TestCase):
    """Unittest for order item model"""

    def setUp(self):
        """set up for unittest"""
        user = User.objects.create(username='username', password='password')
        shop = ShopProfileModel.objects.create(account=user, profile_photo='/orders/tests/sample.jpg',
                                               cover_photo='/orders/tests/sample.jpg', phone_number=123,
                                               description='text', shop_type='F', name='shop',
                                               slug='shop', currency='$', delivery_fee=0,
                                               opens_at=timezone.now() - timezone.timedelta(hours=2),
                                               closes_at=timezone.now() + timezone.timedelta(hours=2),
                                               time_to_prepare=20, vat=14)
        self.product = ProductModel.objects.create(shop=shop, photo='/orders/tests/sample.jpg',
                                                   title='product', slug='product', price=5,
                                                   description='text')
        self.addon1 = AddOnModel.objects.create(product=self.product, title='addon1', added_price=5)
        self.addon2 = AddOnModel.objects.create(product=self.product, title='addon2', added_price=11)

        self.option_group1 = OptionGroupModel.objects.create(product=self.product, title='group1',
                                                             changes_price=True)
        self.option1 = OptionModel.objects.create(option_group=self.option_group1, title='option1',
                                                  price=3.2)
        self.option2 = OptionModel.objects.create(option_group=self.option_group1, title='option2',
                                                  price=5.7)

        self.option_group2 = OptionGroupModel.objects.create(product=self.product, title='group2',
                                                             changes_price=False)
        self.option3 = OptionModel.objects.create(option_group=self.option_group2, title='option1')
        self.option4 = OptionModel.objects.create(option_group=self.option_group2, title='option2')

    def test_str(self):
        """test for string function"""
        order_item = OrderItemModel.objects.create()
        self.assertNotEqual(order_item.__str__(), self.product.title)  # because product is null

        order_item = OrderItemModel.objects.create(product=self.product)
        self.assertEqual(order_item.__str__(), self.product.title)

    def test_addons_total_price(self):
        """test for get_add_ons_price function"""
        order_item = OrderItemModel.objects.create(product=self.product)

        order_item.add_ons.add(self.addon1)
        self.assertEqual(order_item.get_add_ons_price(), 5)

        order_item.add_ons.add(self.addon2)
        self.assertEqual(order_item.get_add_ons_price(), 16)

        order_item.add_ons.remove(self.addon1)
        self.assertEqual(order_item.get_add_ons_price(), 11)

    def test_total_price(self):
        """test for get_item_price function"""
        order_item = OrderItemModel.objects.create(product=self.product)
        Choice.objects.create(order_item=order_item, option_group=self.option_group1,
                              choosed_option=self.option1)
        Choice.objects.create(order_item=order_item, option_group=self.option_group2,
                              choosed_option=self.option3)
        order_item.add_ons.add(self.addon1)

        self.assertEqual(order_item.get_item_price(), 5 + 3.2)

        order_item = OrderItemModel.objects.create(product=self.product)
        Choice.objects.create(order_item=order_item, option_group=self.option_group2,
                              choosed_option=self.option3)
        order_item.add_ons.add(self.addon2)

        self.assertEqual(order_item.get_item_price(), 11 + 5)

    def test_vat(self):
        """test for calculate_vat function"""
        order_item = OrderItemModel.objects.create(product=self.product)
        Choice.objects.create(order_item=order_item, option_group=self.option_group2,
                              choosed_option=self.option3)
        order_item.add_ons.add(self.addon2)
        # price without VAT = 16, shop's vat percentage = 14

        self.assertEqual(order_item.calculate_vat(), 2.24)


class TestOrderAddress(TestCase):
    """Unittest for orders address model"""

    def test_str(self):
        """test for string function
        this test is commented out because the
        function responsible for it in signals.py need internet connection.
        """

        # address = OrderAddressModel.objects.create(area='area', type='A', street='street', building='building',
        #                                           location_longitude=30, location_latitude=30)
        # # Egypt, Matrouh generated by signals by geo-reversing location coordinates (30, 30)
        # self.assertEqual(address.__str__(), 'Egypt, Matrouh, area, street, building')


class TestOrderItemChoice(TestCase):
    """Unitest for order item choice"""

    def setUp(self):
        """set up for unittest"""
        user = User.objects.create(username='username', password='password')
        shop = ShopProfileModel.objects.create(account=user, profile_photo='/orders/tests/sample.jpg',
                                               cover_photo='/orders/tests/sample.jpg', phone_number=123,
                                               description='text', shop_type='F', name='shop',
                                               slug='shop', currency='$', delivery_fee=0,
                                               opens_at=timezone.now() - timezone.timedelta(hours=2),
                                               closes_at=timezone.now() + timezone.timedelta(hours=2),
                                               time_to_prepare=20, vat=14)
        product = ProductModel.objects.create(shop=shop, photo='/orders/tests/sample.jpg',
                                              title='product', slug='product', price=5,
                                              description='text')

        self.option_group1 = OptionGroupModel.objects.create(product=product, title='group1',
                                                             changes_price=True)
        self.option1 = OptionModel.objects.create(option_group=self.option_group1, title='option1',
                                                  price=3.2)

    def test_str(self):
        """test for string function"""

        choice = Choice.objects.create(option_group=self.option_group1, choosed_option=self.option1)
        self.assertEqual(choice.__str__(), 'group1: option1')

        choice = Choice.objects.create()
        self.assertNotEqual(choice.__str__(), 'group1: option1')
