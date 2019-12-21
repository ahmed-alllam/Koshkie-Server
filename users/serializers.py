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
        user = User.objects.create(**user_data, username=user_data['email'])
        user_profile = UserProfileModel.objects.create(user=user, **validated_data)
        return user_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        user_data = validated_data.pop('user')
        user = instance.user
        user.first_name = user_data.get('first_name', user.first_name)
        user.last_name = user_data.get('last_name', user.last_name)
        user.email = user_data.get('email', user.email)
        user.username = user_data.get('email', user.username)
        user.set_password(user_data.get('password', user.password))
        user.save()

        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddressModel
        exclude = 'user'
        extra_kwargs = {
            'id': {'read_only': True},
            'special_notes': {'required': False}
        }
