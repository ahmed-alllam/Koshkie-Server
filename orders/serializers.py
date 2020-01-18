#  Copyright (c) Code Written and Tested by Ahmed Emad in 18/01/2020, 20:11
from math import acos, cos, sin, radians

from django.db.models import F
from rest_framework import serializers

from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice, OrderAddressModel, OrderItemsGroupModel
from shops.models import ProductModel
from shops.serializers import (ShopProfileSerializer, ProductSerializer,
                               AddOnSerializer, OptionGroupSerializer, OptionSerializer)
from users.serializers import UserProfileSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    option_group = OptionGroupSerializer(read_only=True, keep_only=('sort', 'title'))
    option_group_id = serializers.IntegerField(write_only=True)
    choosed_option = OptionSerializer(read_only=True, keep_only=('sort', 'title'))
    choosed_option_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Choice
        fields = ('option_group', 'option_group_id', 'choosed_option', 'choosed_option_id')


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddressModel
        exclude = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    ordered_product = ProductSerializer(read_only=True, keep_only=('id', 'title'))
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
        product = data['product']
        add_ons = data.get('add_ons_sorts', [])
        choices = data.get('choices', [])

        if add_ons:
            for add_on in add_ons:
                if not product.add_ons.filter(sort=add_on).exists():
                    raise serializers.ValidationError("add-on Doesn't Exist")

        if choices:
            seen = []
            for choice in choices:
                if choice in seen:
                    raise serializers.ValidationError("duplicate choices for the order item")
                seen.append(choice)

                if product.option_groups.filter(sort=choice.get('option_group_id')).exists():
                    if not product.option_groups.get(sort=choice.get('option_group_id')).options.filter(
                            sort=choice.get('choosed_option_id')).exists():
                        raise serializers.ValidationError("chosen option doesn't exist")
                else:
                    raise serializers.ValidationError("option group doesn't exist")

        def _is_choosed(group, option):
            for choice_dict in choices:
                if choice_dict.get('option_group_id') == group and choice_dict.get('choosed_option_id') == option:
                    return True
            return False

        for option_group in product.option_groups.all():
            if option_group.sort in [choice.get('option_group_id') for choice in choices]:
                if hasattr(option_group, 'rely_on') and not _is_choosed(option_group.rely_on.choosed_option_group.sort,
                                                                        option_group.rely_on.option.sort):
                    raise serializers.ValidationError("the rely-on required for this option group is not chosen")
            else:
                if not hasattr(option_group, 'rely_on') or (hasattr(option_group, 'rely_on') and _is_choosed(
                        option_group.rely_on.choosed_option_group.sort,
                        option_group.rely_on.option.sort)):
                    raise serializers.ValidationError("not all required option groups are chosen")
        return data


class OrderItemsGroupSerializer(serializers.ModelSerializer):
    shop = ShopProfileSerializer(read_only=True, keep_only=('profile_photo',
                                                            'name', 'address'))
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItemsGroupModel
        fields = ('shop', 'items')


class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    item_groups = OrderItemsGroupSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, write_only=True)
    shipping_address = OrderAddressSerializer()

    class Meta:
        model = OrderModel
        fields = ('id', 'user', 'driver', 'items', 'item_groups', 'ordered_at', 'shipping_address',
                  'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('id', 'user', 'driver', 'ordered_at',
                            'final_price', 'delivery_fee', 'vat')

    def validate(self, attrs):
        for item in attrs['items']:
            product = item['product']
            shop = product.shop
            shops = []
            if shop not in shops:
                shops.append(shop)
                shop_longitude = shop.address.location_longitude
                shop_latitude = shop.address.location_latitude
                user_longitude = attrs['shipping_address']['location_longitude']
                user_latitude = attrs['shipping_address']['location_latitude']
                distance = 6367 * acos(cos(radians(float(user_latitude))) *
                                       cos(radians(shop_longitude)) *
                                       cos(radians(shop_latitude) -
                                           radians(float(user_longitude))
                                           ) +
                                       sin(radians(float(user_latitude))) *
                                       sin(radians(shop_latitude))
                                       )
                if distance > 2.5:
                    raise serializers.ValidationError("these products are not available in you area")
        return attrs

    def create(self, validated_data):
        validated_data.pop('arrived', None)

        items_data = validated_data.pop('items')
        items = list()

        shops = set()
        item_groups = set()
        delivery_fee = 0
        vat = 0
        subtotal = 0

        for item in items_data:
            choices = item.pop('choices', [])
            add_ons_ids = item.pop('add_ons_sorts', [])
            order_item = OrderItemModel.objects.create(**item)
            order_item.product.num_sold.update(num_sold=F('num_sold') + 1)
            for choice in choices:
                option_group = order_item.product.option_groups.get(sort=choice['option_group_id'])
                choosed_option = option_group.options.get(sort=choice['choosed_option_id'])
                Choice.objects.create(order_item=order_item, option_group=option_group,
                                      choosed_option=choosed_option)
            for add_on_id in add_ons_ids:
                add_on = order_item.product.add_ons.get(sort=add_on_id)
                order_item.add_ons.add(add_on)
            order_item.price = order_item.get_item_price()
            items.append(order_item)
            shop = order_item.get_shop()
            if shop not in shops:
                shops.add(shop)
                delivery_fee += shop.delivery_fee

                item_group = OrderItemsGroupModel.objects.create(shop=shop)
                item_groups.add(item_group)
            else:
                item_group = [x for x in item_groups if x.shop == shop][0]

            order_item.item_group = item_group

            vat += order_item.calculate_vat()
            subtotal += order_item.get_item_price()
            order_item.save()

        final_price = subtotal + vat + delivery_fee

        address_data = validated_data.pop('shipping_address')
        shipping_address = OrderAddressModel.objects.create(**address_data)

        order = OrderModel.objects.create(delivery_fee=delivery_fee, vat=vat, subtotal=subtotal,
                                          shipping_address=shipping_address, final_price=final_price,
                                          **validated_data)
        order.shops.set(shops)
        order.item_groups.set(item_groups)
        return order

    def update(self, instance, validated_data):
        # make edits to status too
        if not instance.arrived:
            instance.arrived = validated_data.get('arrived', False)
            instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    driver = DriverProfileSerializer()
    shops = ShopProfileSerializer(many=True, keep_only=('profile_photo', 'name'))

    class Meta:
        model = OrderModel
        fields = ('id', 'user', 'driver', 'shops', 'ordered_at', 'arrived', 'final_price')
