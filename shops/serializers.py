from rest_framework import serializers

from shops.models import (ShopProfileModel, ProductGroupModel, ProductModel,
                          OptionGroupModel, OptionModel, AddOn, RelyOn,
                          ShopAddressModel, ShopReviewModel, ProductReviewModel)


# done


class ShopProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopProfileModel
        fields = ('profile_photo', 'phone_number', 'shop_type', 'name', 'rating', 'is_open', 'currency',
                  'minimum_charge', 'delivery_fee', 'vat')
        extra_kwargs = {
            'rating': {'read_only': True},
            'is_open': {'write_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ('photo', 'title', 'description', 'base_price', 'is_available')
        extra_kwargs = {
            'is_available': {'write_only': True}
        }


class ProductGroupSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ProductGroupModel
        depth = 1
        fields = ('title', 'sort', 'products')


class OptionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionGroupModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class RelyOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelyOn
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


# done


class ShopAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAddressModel
        exclude = 'shop'
        extra_kwargs = {
            'special_notes': {'required': False}
        }


# done


class ShopReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


# done


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }
