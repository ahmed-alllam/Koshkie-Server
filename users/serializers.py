from django.contrib.auth.models import User
from rest_framework import serializers

from users.models import UserProfileModel, UserAddressModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfileModel
        fields = ('user', 'profile_photo', 'phone_number')
        extra_kwargs = {
            'profile_photo': {'required': False},
            'phone_number': {'required': False}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        user_profile = UserProfileModel.objects.create(user=user, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        pass


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = 'user'
        extra_kwargs = {
            'special_notes': {'required': False}
        }

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
