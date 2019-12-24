#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.contrib.auth.models import User
from rest_framework import serializers

from drivers.models import DriverProfileModel, DriverReviewModel
from users.serializers import UserProfileSerializer, UserSerializer


class DriverProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = DriverProfileModel
        fields = ('user', 'profile_photo', 'phone_number', 'vehicle_type', 'rating')
        extra_kwargs = {
            'rating': {'read_only': True}
        }

    def validate_vehicle_type(self, data):
        types = {"car", "bike", "motorcycle"}

        matches = False
        for vehicle_type in types:
            if data.lower() == vehicle_type: matches = True

        if not matches:
            raise serializers.ValidationError('invalid shop type')

        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, username=user_data['email'])
        driver_profile = DriverProfileModel.objects.create(user=user, **validated_data)
        return driver_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
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


class DriverReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = DriverReviewModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        extra_kwargs = {
            'time_stamp': {'read_only': True},
        }
