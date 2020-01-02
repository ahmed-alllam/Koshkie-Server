#  Copyright (c) Code Written and Tested by Ahmed Emad in 02/01/2020, 20:19

from django.contrib.auth.models import User
from rest_framework import serializers

from drivers.models import DriverProfileModel, DriverReviewModel
from users.serializers import UserProfileSerializer, UserSerializer


class DriverProfileSerializer(serializers.ModelSerializer):
    account = UserSerializer()

    class Meta:
        model = DriverProfileModel
        fields = ('id', 'account', 'profile_photo', 'phone_number', 'vehicle_type', 'rating')
        extra_kwargs = {
            'id': {'read_only': True},
            'rating': {'read_only': True}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('account')
        account = User.objects.create(**user_data)
        driver_profile = DriverProfileModel.objects.create(account=account, **validated_data)
        return driver_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
        instance.save()

        user_data = validated_data.pop('account', {})
        account = instance.account
        account.first_name = user_data.get('first_name', account.first_name)
        account.last_name = user_data.get('last_name', account.last_name)
        account.save()

        return instance


class DriverReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = DriverReviewModel
        fields = ('sort', 'user', 'stars', 'text', 'time_stamp')
        extra_kwargs = {
            'sort': {'read_only': True},
            'time_stamp': {'read_only': True},
        }

    def validate_stars(self, stars):
        decimal_digits = str(stars - int(stars))[2:]
        print(decimal_digits)
        if len(decimal_digits) > 1 or int(decimal_digits) % 5 != 0:
            raise serializers.ValidationError("invalid number of stars")
        return stars

    def create(self, validated_data):
        driver = validated_data['driver']
        review = DriverReviewModel(**validated_data)
        latest_sort = driver.reviews.count()
        review.sort = latest_sort + 1
        review.save()

        driver.calculate_rating()
        driver.save()

        return review

    def update(self, instance, validated_data):
        instance.stars = validated_data.get('stars', instance.stars)
        instance.text = validated_data.get('text', instance.text)
        instance.save()

        instance.driver.calculate_rating()
        instance.driver.save()
        return instance
