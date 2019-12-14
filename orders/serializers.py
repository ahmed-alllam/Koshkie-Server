from rest_framework import serializers

from accounts.serializers import UserProfileSerializer, UserAddressSerializer
from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice
from shops.serializers import ShopProfileDetailSerializer, ProductSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('option_group', 'choosed_option')
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = OrderItemModel
        fields = ('product', 'quantity', 'add_ons', 'special_request')
        depth = 1
        extra_kwargs = {
            'special_request': {'required': False}
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)
    driver = DriverProfileSerializer(many=False, read_only=True)
    shops = ShopProfileDetailSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = UserAddressSerializer(many=False, read_only=True)

    class Meta:
        model = OrderModel
        fields = ('user', 'driver', 'shops', 'items', 'ordered_at', 'shipping_address',
                  'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('user', 'driver', 'shops', 'ordered_at',
                            'arrived', 'final_price', 'delivery_fee', 'vat')
        depth = 2
