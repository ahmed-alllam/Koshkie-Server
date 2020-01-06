#  Copyright (c) Code Written and Tested by Ahmed Emad in 06/01/2020, 16:28

from django.contrib.auth.models import User
from rest_framework import serializers

from shops.models import (ShopProfileModel, ProductGroupModel, ProductModel,
                          OptionGroupModel, OptionModel, AddOn, RelyOn,
                          ShopAddressModel, ShopReviewModel, ProductReviewModel)
from users.serializers import UserProfileSerializer, UserSerializer


class RelyOnSerializer(serializers.ModelSerializer):
    choosed_option_group = serializers.IntegerField(source='choosed_option_group.sort')
    option = serializers.IntegerField(source='option.sort')

    class Meta:
        model = RelyOn
        fields = ('choosed_option_group', 'option')


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
        RelyOn.objects.create(option_group=option_group,
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
        fields = ('sort', 'user', 'stars', 'text', 'time_stamp')
        extra_kwargs = {
            'sort': {'read_only': True},
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ProductDetailsSerializer(serializers.ModelSerializer):
    option_groups = OptionGroupSerializer(many=True, read_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductModel
        fields = ('slug', 'photo', 'title', 'description', 'price', 'is_available',
                  'rating', 'option_groups', 'add_ons')
        extra_kwargs = {
            'slug': {'read_only': True},
            'rating': {'read_only': True}
        }

    def to_representation(self, instance):
        data = super(ProductDetailsSerializer, self).to_representation(instance)
        data.update(reviews_count=instance.reviews.count())
        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ('slug', 'photo', 'title', 'price', 'rating')

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)

        super(ProductSerializer, self).__init__(*args, **kwargs)

        # to exclude price field if there are option groups that change price
        if exclude is not None:
            not_allowed = set(exclude)
            for exclude_name in not_allowed:
                self.fields.pop(exclude_name)


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
        exclude = ('shop', 'id')
        extra_kwargs = {
            'special_notes': {'required': False},
        }


class ShopReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = ShopReviewModel
        fields = ('sort', 'user', 'stars', 'text', 'time_stamp')
        extra_kwargs = {
            'sort': {'read_only': True},
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }


class ShopProfileDetailSerializer(serializers.ModelSerializer):
    account = UserSerializer()
    address = ShopAddressSerializer()
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ShopProfileModel
        fields = ('slug', 'account', 'profile_photo', 'phone_number', 'description', 'shop_type',
                  'name', 'address', 'rating', 'reviews_count', 'is_open', 'opens_at', 'closes_at',
                  'currency', 'minimum_charge', 'delivery_fee', 'vat')
        extra_kwargs = {
            'slug': {'read_only': True},
            'rating': {'read_only': True},
            'reviews_count': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)

        super(ShopProfileDetailSerializer, self).__init__(*args, **kwargs)

        # to exclude account field
        if exclude is not None:
            self.fields.pop(exclude)

    def to_representation(self, instance):
        data = super(ShopProfileDetailSerializer, self).to_representation(instance)
        data.update(reviews_count=instance.reviews.count())
        return data

    def create(self, validated_data):
        address_data = validated_data.pop('address')

        account_data = validated_data.pop('account')
        account = User.objects.create(**account_data)

        shop_profile = ShopProfileModel.objects.create(account=account, **validated_data)

        ShopAddressModel.objects.create(shop=shop_profile, **address_data)

        return shop_profile

    def update(self, instance, validated_data):
        excluded = {'slug', 'account', 'rating', 'address', 'reviews_count'}
        attrs = [x for x in self.fields if x not in excluded]
        for attr in attrs:
            setattr(instance, attr, validated_data.get(attr, getattr(instance, attr)))

        instance.save()

        address_data = validated_data.pop('address', {})
        address = instance.address
        address.area = address_data.get('area', address.area)
        address.street = address_data.get('street', address.street)
        address.building = address_data.get('building', address.building)
        address.special_notes = address_data.get('special_notes', address.special_notes)
        address.location_longitude = address_data.get('location_longitude', address.location_longitude)
        address.location_latitude = address_data.get('location_latitude', address.location_latitude)
        address.save()

        account_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = account_data.get('first_name', account.first_name)
        account.last_name = account_data.get('last_name', account.last_name)
        account.username = account_data.get('username', account.username)
        account.set_password(account_data.get('password', account.password))

        account.save()

        return instance


class ShopProfileSerializer(serializers.ModelSerializer):
    address = ShopAddressSerializer()

    class Meta:
        model = ShopProfileModel
        fields = ('slug', 'profile_photo', 'shop_type', 'name', 'address', 'rating')
