#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from rest_framework import viewsets

from users.models import UserProfileModel
from users.serializers import UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfileModel.objects.all()
    serializer_class = UserProfileSerializer
