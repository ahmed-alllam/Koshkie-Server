from rest_framework import serializers

from drivers.serializers import DriverProfileSerializer
from orders.models import OrderModel, OrderItemModel, Choice
from shops.serializers import ShopProfileSerializer, ProductSerializer
from users.serializers import UserProfileSerializer, UserAddressSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('option_group', 'choosed_option')


class OrderItemSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)
    product = ProductSerializer()

    # don't add a field for add-ons , because it is flat

    class Meta:
        model = OrderItemModel
        fields = ('product', 'quantity', 'choices', 'add_ons', 'special_request')
        extra_kwargs = {
            'special_request': {'required': False}
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)
    shops = ShopProfileSerializer(many=True, read_only=True)
    items = OrderItemSerializer(many=True)
    shipping_address = UserAddressSerializer()

    class Meta:
        model = OrderModel
        fields = ('user', 'driver', 'shops', 'items', 'ordered_at', 'shipping_address',
                  'arrived', 'final_price', 'delivery_fee', 'vat')
        read_only_fields = ('user', 'driver', 'shops', 'ordered_at',
                            'arrived', 'final_price', 'delivery_fee', 'vat')
