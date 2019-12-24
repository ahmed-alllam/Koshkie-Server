#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.contrib.auth.models import User
from rest_framework import serializers

from shops.models import (ShopProfileModel, ProductGroupModel, ProductModel,
                          OptionGroupModel, OptionModel, AddOn, RelyOn,
                          ShopAddressModel, ShopReviewModel, ProductReviewModel)
from users.serializers import UserProfileSerializer, UserSerializer


class RelyOnSerializer(serializers.ModelSerializer):
    choosed_option_group = serializers.IntegerField()
    option = serializers.IntegerField()

    class Meta:
        model = RelyOn
        fields = ('choosed_option_group', 'option')

    def to_representation(self, instance):
        return {
            'choosed_option_group': instance.choosed_option_group.sort,
            'option': instance.option.sort
        }


class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = ('title', 'sort', 'added_price')
        extra_kwargs = {
            'sort': {'read_only': True}
        }


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionModel
        fields = ('title', 'sort', 'price')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def validated_price(self, data):
        option_group = self.context['option_group']
        if data > 0 and not option_group.changes_price:
            raise serializers.ValidationError("option group does't change product's price")
        if data <= 0 and option_group.changes_price:
            raise serializers.ValidationError("option must have price")
        return data


class OptionGroupSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    rely_on = RelyOnSerializer(required=False)

    class Meta:
        model = OptionGroupModel
        fields = ('options', 'title', 'sort', 'changes_price', 'rely_on')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def validated_changes_price(self, data):
        product = self.context['product']
        if product.option_groups.filter(changes_price=True).exists():
            raise serializers.ValidationError("""A Product Can't have multiple price
                                                 changing option group""")
        return data

    def validate_rely_on(self, data):
        product = self.context['product']
        option_group_qs = product.option_groups.filter(sort=data['choosed_option_group'])
        if option_group_qs.exists():
            if not option_group_qs.get().options.filter(sort=data['option']).exists():
                raise serializers.ValidationError("option doesn't exist")
        else:
            raise serializers.ValidationError("option group doesn't exist")

        return data

    def create(self, validated_data):
        product = self.context['product']

        rely_on_data = validated_data.pop('rely_on')

        option_group = OptionGroupModel.objects.create(**validated_data)

        choosed_option_group = product.option_groups.get(sort=rely_on_data['choosed_option_group'])
        option = choosed_option_group.options.get(sort=rely_on_data['option'])
        rely_on = RelyOn.objects.create(option_group=option_group,
                                        choosed_option_group=choosed_option_group, option=option)

        return option_group

    def update(self, instance, validated_data):
        product = self.context['product']

        rely_on_data = validated_data.pop('rely_on')
        rely_on = instance.rely_on
        rely_on.choosed_option_group = product.option_groups.get(
            sort=rely_on_data.get('choosed_option_group',
                                  rely_on.choosed_option_group.sort))
        rely_on.option = rely_on.options.get(sort=rely_on_data.get('option', rely_on.option.sort))
        rely_on.save()

        instance.title = validated_data.get('title', instance.title)
        instance.save()

        return instance


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = ProductReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ProductDetailsSerializer(serializers.ModelSerializer):
    option_groups = OptionGroupSerializer(many=True, read_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True)

    class Meta:
        model = ProductModel
        fields = ('id', 'photo', 'title', 'description', 'price', 'is_available', 'rating',
                  'option_groups', 'add_ons')
        extra_kwargs = {
            'id': {'read_only': True},
            'rating': {'read_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    option_groups = OptionGroupSerializer(many=True, required=False)
    add_ons = AddOnSerializer(many=True, required=False)

    class Meta:
        model = ProductModel
        fields = ('id', 'photo', 'title', 'price', 'rating', 'option_groups', 'add_ons')
        extra_kwargs = {
            'id': {'read_only': True},
            'rating': {'read_only': True}
        }


class ProductGroupSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ProductGroupModel
        fields = ('title', 'sort', 'products')
        extra_kwargs = {
            'sort': {'read_only': True}
        }


class ShopAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAddressModel
        exclude = 'shop'
        extra_kwargs = {
            'special_notes': {'required': False}
        }


class ShopReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ShopReviewModel
        fields = ('user', 'stars', 'title', 'text', 'time_stamp')
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ShopProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    address = ShopAddressSerializer()
    in_favourites_list = serializers.BooleanField(read_only=True)

    class Meta:
        model = ShopProfileModel
        fields = ('id', 'user', 'profile_photo', 'phone_number', 'description', 'shop_type',
                  'name', 'address', 'rating', 'is_open', 'opens_at', 'closes_at', 'currency',
                  'minimum_charge', 'delivery_fee', 'vat')
        extra_kwargs = {
            'id': {'read_only': True},
            'rating': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)

        super(ShopProfileDetailSerializer, self).__init__(*args, **kwargs)

        if exclude is not None:
            not_allowed = set(exclude)
            for exclude_name in not_allowed:
                self.fields.pop(exclude_name)

    def validate_shop_type(self, data):
        types = {"food", "pharmacy", "groceries"}

        matches = False
        for shop_type in types:
            if data.lower() == shop_type: matches = True

        if not matches:
            raise serializers.ValidationError('invalid shop type')

        return data

    def validate_currency(self, data):
        currencies = {"egp", "dollar", "euro"}

        matches = False
        for currency in currencies:
            if data.lower() == currency: matches = True

        if not matches:
            raise serializers.ValidationError('invalid currency')

        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        shop_address = ShopAddressModel.objects.create(**address_data)

        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)

        shop_profile = ShopProfileModel.objects.create(user=user, address=shop_address,
                                                       **validated_data)

        return shop_profile

    def update(self, instance, validated_data):
        attrs = self.fields - ('id', 'user', 'rating', 'address')
        for attr in attrs:
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))

        instance.save()

        address_data = validated_data.pop('address')
        address = instance.address
        address.area = address_data.get('area', address.area)
        address.street = address_data.get('street', address.street)
        address.building = address_data.get('building', address.building)
        address.special_notes = address_data.get('special_notes', address.special_notes)
        address.location_longitude = address_data.get('location_longitude', address.location_longitude)
        address.location_latitude = address_data.get('location_latitude', address.location_latitude)
        address.save()

        user_data = validated_data.pop('user')
        user = instance.user
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.username = user_data.get('email', user.username)
        user.set_password(user_data.get('password', user.password))
        user.save()

        return instance


class ShopProfileSerializer(serializers.ModelSerializer):
    address = ShopAddressSerializer()

    class Meta:
        model = ShopProfileModel
        fields = ('profile_photo', 'shop_type', 'name', 'address', 'rating')
