from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import UserProfileModel, UserAddressModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileModel
        fields = ('profile_photo', 'phone_number')
        extra_kwargs = {
            'profile_photo': {'required': False},
            'phone_number': {'required': False}
        }


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = 'user'
