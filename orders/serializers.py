from rest_framework import serializers

from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice
from shops.models import ProductModel
from shops.serializers import ShopProfileSerializer, ProductSerializer
from users.models import UserAddressModel
from users.serializers import UserProfileSerializer, UserAddressSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('option_group', 'choosed_option')


class OrderItemSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                    queryset=ProductModel.objects.all())

    add_ons = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = OrderItemModel
        fields = ('product', 'product_id', 'quantity', 'choices', 'add_ons', 'special_request')
        extra_kwargs = {
            'special_request': {'required': False},
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    shops = ShopProfileSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True)
    shipping_address = UserAddressSerializer(read_only=True)
    shipping_address_id = serializers.PrimaryKeyRelatedField(write_only=True,
                                                             queryset=UserAddressModel.objects.all())

    class Meta:
        model = OrderModel
        fields = ('user', 'driver', 'shops', 'items', 'ordered_at', 'shipping_address',
                  'shipping_address_id', 'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('user', 'driver', 'shops', 'ordered_at',
                            'arrived', 'final_price', 'delivery_fee', 'vat')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        items = list()

        for item in items_data:
            choices = item.pop('choices')
            order_item = OrderItemModel.objects.create(**item)
            for choice in choices:
                Choice.objects.create(order_item=order_item, **choice)
            items.append(order_item)

        shops = set()
        delivery_fee = 0
        vat = 0
        subtotal = 0

        for item in items:
            shops.add(item.get_shop())
            vat += item.calculate_vat()
            subtotal += item.get_item_price()

        for shop in shops:
            delivery_fee += shop.delivery_fee

        final_price = subtotal + vat + delivery_fee

        order = OrderModel.objects.create(items=items, shops=list(shops), delivery_fee=delivery_fee,
                                          vat=vat, subtotal=subtotal,
                                          final_price=final_price, **validated_data)
        return order

    def update(self, instance, validated_data):
        if not instance.arrived:
            instance.arrived = validated_data.get('arrived', False)
