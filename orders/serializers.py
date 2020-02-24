#  Copyright (c) Code Written and Tested by Ahmed Emad in 24/02/2020, 12:36

from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from drivers.models import DriverProfileModel
from drivers.serializers import DriverProfileSerializer
from koshkie import haversine
from orders.models import OrderModel, OrderItemModel, Choice, OrderAddressModel, OrderItemsGroupModel
from shops.models import ProductModel
from shops.serializers import (ShopProfileSerializer, ProductSerializer,
                               AddOnSerializer, OptionGroupSerializer, OptionSerializer)
from users.serializers import UserProfileSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    """The serializer for the order item choices model"""

    option_group = OptionGroupSerializer(read_only=True, keep_only=('sort', 'title'))
    option_group_id = serializers.IntegerField(write_only=True)
    choosed_option = OptionSerializer(read_only=True, keep_only=('sort', 'title'))
    choosed_option_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Choice
        fields = ('option_group', 'option_group_id', 'choosed_option', 'choosed_option_id')


class OrderAddressSerializer(serializers.ModelSerializer):
    """The serializer for the order address model"""

    class Meta:
        model = OrderAddressModel
        exclude = ('id', 'country', 'city')


class OrderItemSerializer(serializers.ModelSerializer):
    """The serializer for the order item model"""

    ordered_product = ProductSerializer(read_only=True, keep_only=('id', 'title'), source='product')
    product = serializers.PrimaryKeyRelatedField(write_only=True,
                                                 queryset=ProductModel.objects.all())
    add_ons_sorts = serializers.ListField(child=serializers.IntegerField(), required=False,
                                          write_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True, keep_only=('sort', 'title'))
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = OrderItemModel
        fields = ('ordered_product', 'product', 'quantity', 'price', 'choices', 'add_ons', 'add_ons_sorts',
                  'special_request')
        extra_kwargs = {
            'special_request': {'required': False},
            'price': {'read_only': True}
        }

    def validate(self, data):
        # validates the data passed to the order item

        product = data['product']
        add_ons = data.get('add_ons_sorts', [])
        choices = data.get('choices', [])

        if not product.is_available:  # may be out of order
            raise serializers.ValidationError("this product is not available right now")

        if add_ons:
            for add_on in add_ons:
                if not product.add_ons.filter(sort=add_on).exists():  # checks for add-ons sorts
                    raise serializers.ValidationError("add-on Doesn't Exist")

        if choices:
            seen = []
            for choice in choices:
                if choice in seen:  # for example you can't have choice like (size: big) sent twice
                    raise serializers.ValidationError("duplicate choices for the order item")
                seen.append(choice)

                # checks for option group sorts
                if product.option_groups.filter(sort=choice.get('option_group_id')).exists():
                    # checks for options inside an option group sorts
                    if not product.option_groups.get(sort=choice.get('option_group_id')).options.filter(
                        sort=choice.get('choosed_option_id')).exists():
                        raise serializers.ValidationError("chosen option doesn't exist")
                else:
                    raise serializers.ValidationError("option group doesn't exist")

        def _is_choosed(group, option):
            """checks if an option and option group pair is choosed"""
            for choice_dict in choices:
                if choice_dict.get('option_group_id') == group and choice_dict.get('choosed_option_id') == option:
                    return True
            return False

        for option_group in product.option_groups.all():
            # checks whether all option group in the product are choosed
            if option_group.sort in [choice.get('option_group_id') for choice in choices]:
                #  checks that that option group doesn't have a rely_on
                #  on another option which is not choosed in that item
                if hasattr(option_group, 'rely_on') and not _is_choosed(option_group.rely_on.choosed_option_group.sort,
                                                                        option_group.rely_on.option.sort):
                    raise serializers.ValidationError("the rely-on required for this option group is not chosen")
            else:
                # only option group which have (rely_on which is not choosed) can't be choosed
                # for example if you have an option group called meal type which
                # has two options (with cola, without cola)
                # and there is another option group called cola type
                # which has options (diet cola, sprite)
                # that option group (cola type must have rely on attr which has value
                # of (meal typ :with cola))
                # because if the user choosed without cola, he shouldn't choose the cola type

                if not hasattr(option_group, 'rely_on') or (hasattr(option_group, 'rely_on') and _is_choosed(
                    option_group.rely_on.choosed_option_group.sort,
                    option_group.rely_on.option.sort)):
                    raise serializers.ValidationError("not all required option groups are chosen")
        return data


class OrderItemsGroupSerializer(serializers.ModelSerializer):
    """The serializer for the order items group model"""

    shop = ShopProfileSerializer(read_only=True, keep_only=('profile_photo',
                                                            'name', 'address'))
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItemsGroupModel
        fields = ('shop', 'items')


class OrderDetailSerializer(serializers.ModelSerializer):
    """The Detailed serializer for the orders model"""

    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    item_groups = OrderItemsGroupSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, write_only=True)
    shipping_address = OrderAddressSerializer()

    class Meta:
        model = OrderModel
        fields = ('id', 'user', 'driver', 'items', 'item_groups', 'ordered_at', 'status',
                  'shipping_address', 'final_price', 'delivery_fee', 'vat')

        read_only_fields = ('id', 'user', 'driver', 'ordered_at', 'final_price',
                            'delivery_fee', 'vat')

    def validate(self, attrs):
        """checks if send order data is valid"""

        if not self.instance:
            # does this validation only if the user is creating a new order not updating

            user_longitude = float(attrs.get('shipping_address', '').get('location_longitude', ''))
            user_latitude = float(attrs.get('shipping_address', '').get('location_latitude', ''))

            # checks if there are any drivers available at user's location
            min_active_time = timezone.now() - timezone.timedelta(seconds=10)
            driver_available = DriverProfileModel.objects.annotate(distance=haversine(user_latitude, user_longitude,
                                                                                      F('live_location_latitude'),
                                                                                      F('live_location_longitude'))
                                                                   ).filter(distance__lte=2.5, is_busy=False,
                                                                            is_active=True, is_available=True,
                                                                            last_time_online__gte=min_active_time
                                                                            ).exists()

            if not driver_available:
                raise serializers.ValidationError("there are no drivers in your area")

            # checks if every item's shop is available and near the user's location
            for item in attrs['items']:
                product = item['product']
                shop = product.shop
                shops = []
                if shop not in shops:
                    shops.append(shop)

                    if not shop.is_active or not shop.is_open or shop.opens_at > timezone.now().time() or shop.closes_at < timezone.now().time():
                        raise serializers.ValidationError("this product's shop is not available right now")

                    shop_longitude = shop.address.location_longitude
                    shop_latitude = shop.address.location_latitude
                    distance = haversine(user_latitude, user_longitude, shop_latitude, shop_longitude)
                    if distance > 2.5:
                        raise serializers.ValidationError("these products are not available in you area")
        return attrs

    def validate_status(self, data):
        """validates the status attr in the order send data"""

        status_options = {'C': 1, 'P': 2, 'D': 3}
        # status is update-only and can't change to a previous one
        # for example a delivered order can't be reverted
        # back to a still-preparing order
        if self.instance and status_options[data] - status_options[self.instance.status] < 0:
            raise serializers.ValidationError("can't revert orders status")

        return data

    def create(self, validated_data):
        """Creates a new Order"""

        items_data = validated_data.pop('items')

        shops = set()
        item_groups = set()
        delivery_fee = 0
        vat = 0
        subtotal = 0

        for item in items_data:
            choices = item.pop('choices', [])
            add_ons_ids = item.pop('add_ons_sorts', [])
            order_item = OrderItemModel.objects.create(**item)
            # increase the product's number of sells
            order_item.product.num_sold = F('num_sold') + 1
            order_item.product.save()
            for choice in choices:
                # creates a new choice model with choosed option group and option
                option_group = order_item.product.option_groups.get(sort=choice['option_group_id'])
                choosed_option = option_group.options.get(sort=choice['choosed_option_id'])
                Choice.objects.create(order_item=order_item, option_group=option_group,
                                      choosed_option=choosed_option)
            for add_on_id in add_ons_ids:
                # adds all add-ons to that item
                add_on = order_item.product.add_ons.get(sort=add_on_id)
                order_item.add_ons.add(add_on)
            order_item.price = order_item.get_item_price()
            shop = order_item.product.shop
            if shop not in shops:
                # creates a new item group that for that shop
                shops.add(shop)
                delivery_fee += shop.delivery_fee  # adds the shop's delivery_fee to the orders total

                item_group = OrderItemsGroupModel.objects.create(shop=shop)
                item_groups.add(item_group)
            else:
                # sets the item group of that item if it already exists and in item_groups list
                item_group = [x for x in item_groups if x.shop == shop][0]  # only one shop in that list

            order_item.item_group = item_group
            order_item.save()

            # adds up that item's prices to the whole order
            vat += order_item.calculate_vat()
            subtotal += order_item.get_item_price()

        final_price = subtotal + vat + delivery_fee

        address_data = validated_data.pop('shipping_address')
        shipping_address = OrderAddressModel.objects.create(**address_data)

        user_longitude = float(shipping_address.location_longitude)
        user_latitude = float(shipping_address.location_latitude)
        min_active_time = timezone.now() - timezone.timedelta(seconds=10)
        # gets the nearest driver available
        driver = DriverProfileModel.objects.annotate(distance=haversine(user_latitude, user_longitude,
                                                                        F('live_location_latitude'),
                                                                        F('live_location_longitude'))
                                                     ).filter(distance__lte=2.5, is_busy=False,
                                                              is_active=True, is_available=True,
                                                              last_time_online__gte=min_active_time
                                                              ).order_by('distance')[0]
        # the driver now is busy and CAN'T deliver new orders
        driver.is_busy = True
        driver.save()

        # creates the final order
        order = OrderModel.objects.create(driver=driver, shipping_address=shipping_address,
                                          status='C', final_price=final_price,
                                          delivery_fee=delivery_fee, vat=vat,
                                          subtotal=subtotal, **validated_data)
        order.shops.set(shops)
        order.item_groups.set(item_groups)
        return order

    def update(self, instance, validated_data):
        """Updates the Order"""

        # only order's status can be changed
        status = validated_data.get('status', None)
        if status:
            instance.status = status
            if status == 'D':
                # means that the order is well done and delivered
                # the driver will be marked as not busy and
                # can deliver other orders
                instance.driver.is_busy = False
                instance.driver.update()
            instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    """The list and create serializer for the orders model"""

    user = UserProfileSerializer()
    driver = DriverProfileSerializer()
    shops = ShopProfileSerializer(many=True, keep_only=('profile_photo', 'name'))

    class Meta:
        model = OrderModel
        fields = ('id', 'user', 'driver', 'shops', 'ordered_at', 'status', 'final_price')
