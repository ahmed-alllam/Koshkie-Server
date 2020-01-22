#  Copyright (c) Code Written and Tested by Ahmed Emad in 22/01/2020, 12:09

from django.contrib.auth.models import User
from rest_framework import serializers

from drivers.models import DriverProfileModel, DriverReviewModel
from users.serializers import UserProfileSerializer, UserSerializer


class DriverProfileSerializer(serializers.ModelSerializer):
    account = UserSerializer()
    reviews_count = serializers.IntegerField(read_only=True, source='get_reviews_count')

    class Meta:
        model = DriverProfileModel
        fields = ('id', 'account', 'profile_photo', 'phone_number', 'vehicle_type',
                  'rating', 'reviews_count', 'is_active', 'is_busy', 'last_time_online',
                  'live_location_longitude', 'live_location_latitude')
        extra_kwargs = {
            'id': {'read_only': True},
            'is_busy': {'read_only': True},
            'last_time_online': {'read_only': True},
            'rating': {'read_only': True},
        }

    def create(self, validated_data):
        account_data = validated_data.pop('account')
        account = User(**account_data)
        account.set_password(account.password)
        account.save()

        driver_profile = DriverProfileModel.objects.create(account=account, **validated_data)
        return driver_profile

    def update(self, instance, validated_data):
        instance.profile_photo = validated_data.get('profile_photo', instance.profile_photo)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.vehicle_type = validated_data.get('vehicle_type', instance.vehicle_type)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.live_location_longitude = validated_data.get('live_location_longitude',
                                                              instance.live_location_longitude)
        instance.live_location_latitude = validated_data.get('live_location_latitude',
                                                             instance.live_location_latitude)
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

    def get_reviews_count(self):
        return self.instance.reviews.count()


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
        review = DriverReviewModel.objects.create(**validated_data)

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
