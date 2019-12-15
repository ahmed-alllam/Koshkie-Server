from rest_framework import serializers

from accounts.serializers import UserProfileSerializer
from drivers.models import DriverProfileModel, DriverReviewModel


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfileModel
        fields = ('profile_photo', 'phone_number', 'vehicle_type', 'rating')
        extra_kwargs = {
            'rating': {'read_only': True}
        }


class DriverReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = DriverReviewModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        extra_kwargs = {
            'time_stamp': {'read_only': True},
        }
