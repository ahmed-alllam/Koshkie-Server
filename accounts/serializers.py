from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import UserProfileModel, UserAddressModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileModel
        fields = ('name', 'profile_photo')
        extra_kwargs = {
            'profile_photo': {'required': False}
        }


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = ('user',)
