from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from shops.models import (ShopProfileModel, ProductGroupModel, ProductModel,
                          OptionGroupModel, OptionModel, AddOn, RelyOn,
                          ShopAddressModel, ShopReviewModel, ProductReviewModel)


class RelyOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelyOn
        fields = ('choosed_option_group', 'option')


class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = ('title', 'added_price')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionModel
        fields = ('title', 'price')


class OptionGroupSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = OptionGroupModel
        fields = ('options', 'title', 'changes_price')


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = ProductReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ProductDetailsSerializer(serializers.ModelSerializer):
    # add-ons, options not done
    class Meta:
        model = ProductModel
        fields = ('photo', 'title', 'description', 'base_price', 'is_available')
        extra_kwargs = {
            'is_available': {'write_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ('photo', 'title', 'base_price')


class ProductGroupSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ProductGroupModel
        depth = 1
        fields = ('title', 'sort', 'products')


class ShopAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAddressModel
        exclude = 'shop'
        extra_kwargs = {
            'special_notes': {'required': False}
        }


class ShopReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = ShopReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ShopProfileDetailSerializer(serializers.ModelSerializer):
    address = ShopAddressSerializer(many=False)
    in_favourites_list = serializers.BooleanField(read_only=True, required=False)

    class Meta:
        model = ShopProfileModel
        fields = ('id', 'profile_photo', 'phone_number', 'shop_type', 'name',
                  'address', 'rating', 'is_open', 'currency',
                  'minimum_charge', 'delivery_fee', 'vat')
        extra_kwargs = {
            'id': {'read_only': True},
            'rating': {'read_only': True},
            'is_open': {'write_only': True}
        }
        depth = 1


class ShopProfileSerializer(serializers.ModelSerializer):
    address = ShopAddressSerializer(many=False)

    class Meta:
        model = ShopProfileModel
        fields = ('profile_photo', 'shop_type', 'name', 'address', 'rating')
        extra_kwargs = {
            'rating': {'read_only': True},
        }
        depth = 1
