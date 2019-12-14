from rest_framework import serializers

from orders.models import OrderModel, OrderItemModel, Choice


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderModel
        fields = ('profile_photo', 'phone_number', 'vehicle_type', 'rating')
        extra_kwargs = {
            'rating': {'read_only': True}
        }


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }
