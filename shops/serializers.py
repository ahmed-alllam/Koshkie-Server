#  Copyright (c) Code Written and Tested by Ahmed Emad in 18/01/2020, 20:11

from django.contrib.auth.models import User
from rest_framework import serializers

from shops.models import (ShopProfileModel, ProductGroupModel, ProductModel,
                          OptionGroupModel, OptionModel, AddOnModel, RelyOn,
                          ShopAddressModel, ShopReviewModel, ProductReviewModel)
from users.serializers import UserProfileSerializer, UserSerializer


class RelyOnSerializer(serializers.ModelSerializer):
    choosed_option_group = serializers.IntegerField(source='choosed_option_group.sort', required=False)
    option = serializers.IntegerField(source='option.sort', required=False)

    class Meta:
        model = RelyOn
        fields = ('choosed_option_group', 'option')


class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnModel
        fields = ('sort', 'title', 'added_price')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        keep_only_fields = kwargs.pop('keep_only', None)
        if keep_only_fields is not None:
            new_fields = self.fields
            for field in list(new_fields):
                if field not in keep_only_fields:
                    self.fields.pop(field)

        super(AddOnSerializer, self).__init__(*args, **kwargs)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionModel
        fields = ('sort', 'title', 'price')
        extra_kwargs = {
            'sort': {'read_only': True},
            'price': {'required': False}
        }

    def __init__(self, *args, **kwargs):
        keep_only_fields = kwargs.pop('keep_only', None)
        if keep_only_fields is not None:
            new_fields = self.fields
            for field in list(new_fields):
                if field not in keep_only_fields:
                    self.fields.pop(field)

        super(OptionSerializer, self).__init__(*args, **kwargs)

    def validate_price(self, data):
        option_group = self.context['option_group']

        if data > 0 and not option_group.changes_price:
            raise serializers.ValidationError("option group does't change product's price")
        if data <= 0 and option_group.changes_price:
            raise serializers.ValidationError("option must have price")
        return data

    def to_representation(self, instance):
        if not instance.price:
            value = super(OptionSerializer, self).to_representation(instance)
            value.pop('price', {})
            return value
        return super(OptionSerializer, self).to_representation(instance)


class OptionGroupSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    rely_on = RelyOnSerializer(required=False)

    class Meta:
        model = OptionGroupModel
        fields = ('sort', 'title', 'changes_price', 'rely_on', 'options')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        keep_only_fields = kwargs.pop('keep_only', None)
        if keep_only_fields is not None:
            new_fields = self.fields
            for field in list(new_fields):
                if field not in keep_only_fields:
                    self.fields.pop(field)

        super(OptionGroupSerializer, self).__init__(*args, **kwargs)

    def validate(self, attrs):
        changes_price = attrs.get('changes_price', None)
        rely_on = attrs.get('rely_on', None)

        if rely_on and rely_on != {}:
            if not changes_price and changes_price is not None:
                return attrs
            elif self.instance and not self.instance.changes_price and changes_price is None:
                return attrs
            raise serializers.ValidationError("price changing option group can't have rely on")

        elif rely_on == {}:
            return attrs

        elif rely_on is None:
            if not changes_price:
                return attrs
            if self.instance and self.instance.rely_on:
                raise serializers.ValidationError("price changing option group can't have rely on")

        return attrs

    def validate_changes_price(self, data):
        product = self.context['product']
        if data:
            if product.option_groups.filter(changes_price=True).exists():
                raise serializers.ValidationError("A Product Can't have multiple price changing option group")
        return data

    def validate_rely_on(self, data):
        if ('choosed_option_group' in data) and not ('option' in data):
            raise serializers.ValidationError("option required")
        if not ('choosed_option_group' in data) and ('option' in data):
            raise serializers.ValidationError("option group required")

        if data:
            product = self.context['product']
            option_group_qs = product.option_groups.filter(sort=data['choosed_option_group']['sort'])

            if option_group_qs.exists():
                option_group = option_group_qs.get()
                if self.instance and option_group.sort == self.instance.sort:
                    raise serializers.ValidationError("option group must be different than the current one")

                if not option_group.options.filter(sort=data['option']['sort']).exists():
                    raise serializers.ValidationError("option doesn't exist")
            else:
                raise serializers.ValidationError("option group doesn't exist")

        return data

    def create(self, validated_data):
        product = self.context['product']

        rely_on_data = validated_data.pop('rely_on', {})

        option_group = OptionGroupModel.objects.create(**validated_data)

        if rely_on_data:
            choosed_option_group = product.option_groups.get(sort=rely_on_data['choosed_option_group']['sort'])
            option = choosed_option_group.options.get(sort=rely_on_data['option']['sort'])
            RelyOn.objects.create(option_group=option_group,
                                  choosed_option_group=choosed_option_group, option=option)

        return option_group

    def update(self, instance, validated_data):
        product = self.context['product']

        rely_on_data = validated_data.pop('rely_on', None)

        if rely_on_data is not None and rely_on_data != {}:

            choosed_option_group = product.option_groups.get(
                sort=rely_on_data['choosed_option_group']['sort'])

            option = choosed_option_group.options.get(
                sort=rely_on_data['option']['sort'])

            defaults = {'choosed_option_group': choosed_option_group, 'option': option}
            RelyOn.objects.update_or_create(option_group=instance, defaults=defaults)

        elif rely_on_data == {}:
            if instance.rely_on:
                instance.rely_on.delete()
                instance.rely_on = None

        instance.title = validated_data.get('title', instance.title)
        instance.changes_price = validated_data.get('changes_price', instance.changes_price)
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

    def validate_stars(self, stars):
        decimal_digits = str(stars - int(stars))[2:]
        print(decimal_digits)
        if len(decimal_digits) > 1 or int(decimal_digits) % 5 != 0:
            raise serializers.ValidationError("invalid number of stars")
        return stars

    def create(self, validated_data):
        product = validated_data['product']
        review = ProductReviewModel.objects.create(**validated_data)

        product.calculate_rating()
        product.save()

        return review

    def update(self, instance, validated_data):
        instance.stars = validated_data.get('stars', instance.stars)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        instance.product.calculate_rating()
        instance.product.save()
        return instance


class ProductDetailsSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(write_only=True)
    option_groups = OptionGroupSerializer(many=True, read_only=True)
    add_ons = AddOnSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField(read_only=True, source='get_reviews_count')

    class Meta:
        model = ProductModel
        fields = ('id', 'slug', 'group_id', 'photo', 'title', 'rating', 'reviews_count',
                  'description', 'price', 'is_available', 'option_groups', 'add_ons')
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
            'rating': {'read_only': True}
        }

    def to_representation(self, instance):
        if instance.option_groups.filter(changes_price=True).exists():
            value = super(ProductDetailsSerializer, self).to_representation(instance)
            value.pop('price')
            return value
        return super(ProductDetailsSerializer, self).to_representation(instance)

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class ProductSerializer(serializers.ModelSerializer):
    reviews_count = serializers.SerializerMethodField(read_only=True, source='get_reviews_count')

    class Meta:
        model = ProductModel
        fields = ('id', 'slug', 'photo', 'title', 'price', 'rating', 'reviews_count')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def __init__(self, *args, **kwargs):
        keep_only_fields = kwargs.pop('keep_only', None)
        if keep_only_fields is not None:
            new_fields = self.fields
            for field in list(new_fields):
                if field not in keep_only_fields:
                    self.fields.pop(field)

        super(ProductSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, instance):
        if instance.option_groups.filter(changes_price=True).exists():
            value = super(ProductSerializer, self).to_representation(instance)
            value.pop('price')
            return value

        return super(ProductSerializer, self).to_representation(instance)

    def get_reviews_count(self, obj):
        return obj.reviews.count()


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

    def validate_stars(self, stars):
        decimal_digits = str(stars - int(stars))[2:]
        print(decimal_digits)
        if len(decimal_digits) > 1 or int(decimal_digits) % 5 != 0:
            raise serializers.ValidationError("invalid number of stars")
        return stars

    def create(self, validated_data):
        shop = validated_data['shop']
        review = ShopReviewModel.objects.create(**validated_data)

        shop.calculate_rating()
        shop.save()

        return review

    def update(self, instance, validated_data):
        instance.stars = validated_data.get('stars', instance.stars)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        instance.shop.calculate_rating()
        instance.shop.save()
        return instance


class ShopProfileDetailSerializer(serializers.ModelSerializer):
    account = UserSerializer()
    address = ShopAddressSerializer()
    reviews_count = serializers.SerializerMethodField(read_only=True, source='get_reviews_count')

    class Meta:
        model = ShopProfileModel
        fields = ('slug', 'account', 'profile_photo', 'phone_number', 'description', 'shop_type', 'name',
                  'rating', 'reviews_count', 'is_open', 'opens_at', 'closes_at', 'currency',
                  'minimum_charge', 'delivery_fee', 'vat', 'address')
        extra_kwargs = {
            'slug': {'read_only': True},
            'rating': {'read_only': True},
            'is_open': {'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', None)
        if exclude is not None:
            self.fields.pop(exclude)

        super(ShopProfileDetailSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        address_data = validated_data.pop('address')

        account_data = validated_data.pop('account')
        account = User(**account_data)
        account.set_password(account.password)
        account.save()

        shop_profile = ShopProfileModel.objects.create(account=account, **validated_data)

        ShopAddressModel.objects.create(shop=shop_profile, **address_data)

        return shop_profile

    def update(self, instance, validated_data):

        address_data = validated_data.pop('address', {})
        address = instance.address
        address.update_attrs(**address_data)

        account_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = account_data.get('first_name', account.first_name)
        account.last_name = account_data.get('last_name', account.last_name)
        account.username = account_data.get('username', account.username)
        if account_data.get('password') is not None:
            account.set_password(account_data.get('password'))
        account.save()

        instance.update_attrs(**validated_data)

        return instance

    def get_reviews_count(self, obj):
        return obj.reviews.count()


class ShopProfileSerializer(serializers.ModelSerializer):
    address = ShopAddressSerializer()
    reviews_count = serializers.SerializerMethodField(read_only=True, source='get_reviews_count')

    class Meta:
        model = ShopProfileModel
        fields = ('slug', 'profile_photo', 'shop_type', 'name', 'rating', 'reviews_count', 'address')

    def __init__(self, *args, **kwargs):
        keep_only_fields = kwargs.pop('keep_only', None)
        if keep_only_fields is not None:
            new_fields = self.fields
            for field in list(new_fields):
                if field not in keep_only_fields:
                    self.fields.pop(field)

        super(ShopProfileSerializer, self).__init__(*args, **kwargs)

    def get_reviews_count(self, obj):
        return obj.reviews.count()
