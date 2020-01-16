#  Copyright (c) Code Written and Tested by Ahmed Emad in 16/01/2020, 22:16

from rest_framework import serializers

from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice, OrderAddressModel, OrderItemsGroupModel
from shops.models import ProductModel, OptionModel
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
        # Validate that product's shop is near too
        product = ProductModel.objects.get(id=data['product_id'])
        add_ons = data['add_ons_sorts']
        choices = data['choices']

        for add_on in add_ons:
            if not product.add_ons.filter(sort=add_on).exists():
                raise serializers.ValidationError("add-on Doesn't Exist")

        seen = set()
        for choice in choices:
            if choice in seen:
                raise serializers.ValidationError("duplicate choices for the order item")
            seen.add(choice)

        def is_choosed(group, option):
            for choice_dict in choices:
                if choices.get('option_group_id') == group and choice_dict.get('choosed_option_id') == option:
                    return True
            return False

        def get_option(option_group_sort):
            for choice_dict in choices:
                if choice_dict.get('option_group_id') == option_group_sort:
                    return choice_dict.get('choosed_option_id')

        for option_group in product.option_groups.all():
            if option_group.sort not in [choice.get('option_group_id') for choice in choices]:
                if not option_group.rely_on or is_choosed(option_group.rely_on.choosed_option_group.sort,
                                                          option_group.rely_on.option.sort):
                    raise serializers.ValidationError("not all required option groups are chosen")
            if not OptionModel.objects.filter(sort=get_option(option_group.sort)).exists():
                raise serializers.ValidationError("option doesn't exist")
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
