#  Copyright (c) Code Written and Tested by Ahmed Emad in 23/01/2020, 22:30
from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfileModel, UserAddressModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserProfileSerializer(serializers.ModelSerializer):
    account = UserSerializer()

    class Meta:
        model = UserProfileModel
        fields = ('account', 'profile_photo', 'phone_number')
        extra_kwargs = {
            'profile_photo': {'required': False},
        }

    def create(self, validated_data):
        account_data = validated_data.pop('account')
        account = User(**account_data)
        account.set_password(account.password)
        account.save()

        user_profile = UserProfileModel.objects.create(account=account, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        account_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = account_data.get('first_name', account.first_name)
        account.last_name = account_data.get('last_name', account.last_name)
        account.username = account_data.get('username', account.username)
        if account_data.get('password') is not None:
            account.set_password(account_data.get('password'))
        account.save()

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = ('id', 'user')
        extra_kwargs = {
            'sort': {'read_only': True}
        }

    def create(self, validated_data):
        user = UserProfileModel.objects.get(account__username=validated_data.pop('username'))
        address = UserAddressModel.objects.create(**validated_data, user=user)
        return address
