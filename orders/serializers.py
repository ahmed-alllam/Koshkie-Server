#  Copyright (c) Code Written and Tested by Ahmed Emad in 15/01/2020, 12:16

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
        exclude = ('id', 'order')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True, keep_only=('id', 'title'))
    product_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                    queryset=ProductModel.objects.all())

    add_ons_sorts = serializers.ListField(child=serializers.IntegerField(), required=False,
                                          write_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True, keep_only=('sort', 'title'))
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = OrderItemModel
        fields = ('product', 'product_id', 'quantity', 'choices', 'add_ons', 'add_ons_sorts',
                  'special_request')
        extra_kwargs = {
            'special_request': {'required': False},
        }

    def validate(self, data):
        product = ProductModel.objects.get(id=data['product_id'])
        add_ons = data['add_ons_ids']
        choices = data['choices']

        for add_on in add_ons:
            if not product.add_ons.filter(sort=add_on).exists():
                raise serializers.ValidationError("add-on Doesn't Exist")

        if choices.count() != product.option_groups.count():
            raise serializers.ValidationError("missing choices for required options")

        for choice in choices:
            # to check for duplicates
            seen = set()
            if choice['option_group_id'] in seen:
                raise serializers.ValidationError("duplicate choices for the order item")

            seen.add(choice['option_group_id'])

            query = product.option_groups.filter(sort=choice['option_group_id'])
            if query.exists():
                option_group = query.get()
                if not option_group.options.filter(sort=choice['choosed_option_id']).exists():
                    raise serializers.ValidationError("option  Wrong")

                # rely on validation here
                if option_group.rely_on:
                    key = option_group.rely_on.choosed_option_group.sort
                    value = option_group.rely_on.option.sort
                    required_choice = {'option_group_id': key, 'choosed_option_id': value}
                    if not required_choice.items() <= choices.items():
                        raise serializers.ValidationError("required choice not found")

            else:
                raise serializers.ValidationError("option group not found")

        return data


class OrderItemsGroupSerializer(serializers.ModelSerializer):
    shop = ShopProfileSerializer(read_only=True, keep_only=('profile_photo', 'name', 'address'))
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItemsGroupModel
        fields = ('shop', 'items')


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    items = OrderItemsGroupSerializer(many=True)
    shipping_address = OrderAddressSerializer()

    class Meta:
        model = OrderModel
        fields = ('id', 'user', 'driver', 'items', 'ordered_at', 'shipping_address',
                  'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('id', 'user', 'driver', 'ordered_at',
                            'arrived', 'final_price', 'delivery_fee', 'vat')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        items = list()

        shops = set()
        delivery_fee = 0
        vat = 0
        subtotal = 0

        for item in items_data:
            choices = item.pop('choices')
            add_ons_ids = item.pop('add_ons_ids')
            order_item = OrderItemModel(**item)
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

                item_group = OrderItemsGroupModel(shop=shop).save()
                order_item.item_group = item_group

            vat += order_item.calculate_vat()
            subtotal += order_item.get_item_price()
            order_item.save()

        final_price = subtotal + vat + delivery_fee

        address_data = validated_data.pop('shipping_address')
        shipping_address = OrderAddressModel(**address_data).save()

        order = OrderModel.objects.create(items=items, shops=list(shops), delivery_fee=delivery_fee,
                                          vat=vat, subtotal=subtotal, shipping_address=shipping_address,
                                          final_price=final_price, **validated_data)  # user and
        # driver to added from views
        return order

    def update(self, instance, validated_data):
        if not instance.arrived:
            instance.arrived = validated_data.get('arrived', False)
            instance.save()
        return instance
