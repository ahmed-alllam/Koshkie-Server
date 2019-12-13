from rest_framework import serializers

from drivers.models import DriverProfileModel, DriverReviewModel


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfileModel
        fields = ('name', 'profile_photo', 'vehicle_type', 'rating')
        extra_kwargs = {
            'rating': {'read_only': True}
        }


class DriverReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverReviewModel
        fields = ('user', 'stars', 'text', 'time_stamp')
        depth = 1
        extra_kwargs = {
            'time_stamp': {'read_only': True},
            'user': {'read_only': True}
        }
