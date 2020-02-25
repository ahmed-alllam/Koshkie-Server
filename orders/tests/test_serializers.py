#  Copyright (c) Code Written and Tested by Ahmed Emad in 25/02/2020, 22:30
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from drivers.models import DriverProfileModel
from orders.models import OrderModel
from orders.serializers import OrderDetailSerializer, OrderItemSerializer, OrderAddressSerializer
from shops.models import ShopProfileModel, ProductModel, ShopAddressModel, AddOnModel, OptionGroupModel, OptionModel, \
    RelyOn


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
        # product with option groups and addons
        self.product2 = ProductModel.objects.create(shop=self.shop, photo='/orders/tests/sample.jpg',
                                                    title="product", slug='product2', price=5,
                                                    description='text')
        self.addon = AddOnModel.objects.create(product=self.product2, title='addon1', added_price=5)
        self.option_group = OptionGroupModel.objects.create(product=self.product2, title='group1',
                                                            changes_price=True)
        self.option = OptionModel.objects.create(option_group=self.option_group, title='option1',
                                                 price=3.2)

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
        self.shop_address.location_longitude = 12
        self.shop_address.location_latitude = 54
        self.shop_address.save()

        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())

    def test_shop_available(self):
        """test if product's shop is available"""

        # test for is_active
        self.shop.is_active = False
        self.shop.save()

        # wrong because shop is not active
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())
        # revert it back
        self.shop.is_active = True
        self.shop.save()

        # test for is_open
        self.shop.is_open = False
        self.shop.save()

        # wrong because shop is not active
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())
        # revert it back
        self.shop.is_open = True
        self.shop.save()

        # test for opens_at
        self.shop.opens_at = timezone.now() + timezone.timedelta(hours=2)  # two hours after now (not open yet)
        self.shop.save()

        # wrong because shop is not active
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())
        # revert it back
        self.shop.opens_at = timezone.now() - timezone.timedelta(hours=2)
        self.shop.save()

        # test for closes_at
        self.shop.closes_at = timezone.now() - timezone.timedelta(hours=2)  # closed two hours before now (closed now)
        self.shop.save()

        # wrong because shop is not active
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())
        # revert it back
        self.shop.closes_at = timezone.now() + timezone.timedelta(hours=2)
        self.shop.save()

        # true
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertTrue(serializer.is_valid())

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

    def test_wrong_item_data(self):
        """test if any order item data is wrong"""

        # right
        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertTrue(serializer.is_valid())

        # wrong product pk
        serializer = OrderDetailSerializer(data={'items': [{'product': 221}],  # backer street :)
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertFalse(serializer.is_valid())

    def test_nothing(self):
        """this is NOT a test but i needed this
        function to run with other tests"""

        serializer = OrderDetailSerializer(data={'items': [{'product': self.product.pk},
                                                           {'product': self.product2.pk,
                                                            'choices': [{'option_group_id': self.option_group.sort,
                                                                         'choosed_option_id': self.option.sort}],
                                                            'add_ons_sorts': [self.addon.sort]}],
                                                 'shipping_address': {'area': 'area', 'type': 'A',
                                                                      'street': 'street',
                                                                      'building': 'building',
                                                                      'location_longitude': 30,
                                                                      'location_latitude': 30}})
        self.assertTrue(serializer.is_valid())
        serializer.save()


class TestOrderItem(TestCase):
    """Unittest for order item serializer"""

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
        # a product without any addons or option groups
        self.product = ProductModel.objects.create(shop=self.shop, photo='/orders/tests/sample.jpg',
                                                   title='product', slug='product', price=5,
                                                   description='text')

        # a product with addons and option groups
        self.product2 = ProductModel.objects.create(shop=self.shop, photo='/orders/tests/sample.jpg',
                                                    title="product", slug='product', price=5,
                                                    description='text')

        self.addon1 = AddOnModel.objects.create(product=self.product2, title='addon1', added_price=5)
        self.addon2 = AddOnModel.objects.create(product=self.product2, title='addon2', added_price=11)

        self.option_group1 = OptionGroupModel.objects.create(product=self.product2, title='group1',
                                                             changes_price=True)
        self.option1 = OptionModel.objects.create(option_group=self.option_group1, title='option1',
                                                  price=3.2)
        self.option2 = OptionModel.objects.create(option_group=self.option_group1, title='option2',
                                                  price=5.7)

        self.option_group2 = OptionGroupModel.objects.create(product=self.product2, title='group2',
                                                             changes_price=False)
        self.option3 = OptionModel.objects.create(option_group=self.option_group2, title='option1')
        self.option4 = OptionModel.objects.create(option_group=self.option_group2, title='option2')

    def test_product_exists(self):
        """test if product really exists"""

        # right
        serializer = OrderItemSerializer(data={'product': self.product.pk})
        self.assertTrue(serializer.is_valid())

        # non existing pk for a product
        serializer = OrderItemSerializer(data={'product': 12345})
        self.assertFalse(serializer.is_valid())

    def test_product_available(self):
        """test if a product is marked as not available"""

        # change it temporally
        self.product.is_available = False
        self.product.save()

        # wrong because it is not available
        serializer = OrderItemSerializer(data={'product': self.product.pk})
        self.assertFalse(serializer.is_valid())

        # revert it back
        self.product.is_available = True
        self.product.save()

        # wrong because it is not available
        serializer = OrderItemSerializer(data={'product': self.product.pk})
        self.assertTrue(serializer.is_valid())

    def test_addon_exist(self):
        """test for addons sort exist"""

        # right
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'add_ons_sorts': [self.addon1.sort, self.addon2.sort],
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # wrong addons sorts
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'add_ons_sorts': [123, 898],
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertFalse(serializer.is_valid())

    def test_duplicate_choice(self):
        """test if there are any duplicate choices"""

        # right
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # wrong -- duplicate choices
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort}]})
        self.assertFalse(serializer.is_valid())

    def test_option_group_exist(self):
        """test if option group sort exists"""

        # right
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # wrong option group sort
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': 122,  # wrong
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertFalse(serializer.is_valid())

    def test_option_exist(self):
        """test if option sort exists"""

        # right
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # wrong option group sort
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': 32},  # wrong
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertFalse(serializer.is_valid())

    def test_rely_choosed(self):
        """test if a rely_on choosed or not"""

        # add rely on for test option group2
        RelyOn.objects.create(option_group=self.option_group2,
                              choosed_option_group=self.option_group1, option=self.option1)

        # right and rely_on requirement for option_group2 is fulfilled
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # wrong because rely_on requirement {option_group2: option1} is not fulfilled
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option2.sort},  # not 1
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertFalse(serializer.is_valid())

    def test_missing_choice_for_option_group(self):
        """test if any choices missing for an option
        group in the product"""

        # right and all choices are choosed
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort},
                                                           {'option_group_id': self.option_group2.sort,
                                                            'choosed_option_id': self.option3.sort}]})
        self.assertTrue(serializer.is_valid())

        # missing a choice (option group2 not choosed)
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort}]})
        self.assertFalse(serializer.is_valid())

        # add rely on for test option group2
        RelyOn.objects.create(option_group=self.option_group2,
                              choosed_option_group=self.option_group1, option=self.option1)

        # wrong because it is not choosed and has a rely on {option_group1: option1}
        # which is choosed, which makes it required
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option1.sort}]})
        self.assertFalse(serializer.is_valid())

        # right
        # missing a choice but as option group2 relys on choosing {option_group1: option1}
        # which is no choosed, which is makes it unable to be choosed,
        # no error is thrown
        serializer = OrderItemSerializer(data={'product': self.product2.pk,
                                               'choices': [{'option_group_id': self.option_group1.sort,
                                                            'choosed_option_id': self.option2.sort}]})
        self.assertTrue(serializer.is_valid())


class TestOrderAddress(TestCase):
    """Unittest for order address serializer"""

    def test_address_type(self):
        """test for address type validation"""

        # right
        serializer = OrderAddressSerializer(data={'area': 'area', 'type': 'A', 'street': 'street',
                                                  'building': 'building', 'location_longitude': 30,
                                                  'location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # wrong address type
        serializer = OrderAddressSerializer(data={'area': 'area', 'type': 'wrong', 'street': 'street',
                                                  'building': 'building', 'location_longitude': 30,
                                                  'location_latitude': 30})
        self.assertFalse(serializer.is_valid())

    def test_location_coordinates(self):
        """test for address location validation"""

        # right
        serializer = OrderAddressSerializer(data={'area': 'area', 'type': 'A', 'street': 'street',
                                                  'building': 'building', 'location_longitude': 30,
                                                  'location_latitude': 30})
        self.assertTrue(serializer.is_valid())

        # invalid longitude
        serializer = OrderAddressSerializer(data={'area': 'area', 'type': 'A', 'street': 'street',
                                                  'building': 'building', 'location_longitude': 200,
                                                  'location_latitude': 30})
        self.assertFalse(serializer.is_valid())

        # invalid latitude
        serializer = OrderAddressSerializer(data={'area': 'area', 'type': 'A', 'street': 'street',
                                                  'building': 'building', 'location_longitude': 30,
                                                  'location_latitude': -120})
        self.assertFalse(serializer.is_valid())
