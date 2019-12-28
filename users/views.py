#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019
from django.contrib.auth import login
from rest_framework import viewsets, views, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from users.models import UserAddressModel, UserProfileModel
from users.permissions import IsOwner
from users.serializers import UserProfileSerializer, UserAddressSerializer


@api_view(['POST'])
def create_user_profile(request):
    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_406_NOT_ACCEPTABLE)
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        user_profile = serializer.save()
        login(request, user_profile.account)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_profile(request, pk=None):
    user_profile = get_object_or_404(UserProfileModel, pk=pk)
    serializer = UserProfileSerializer(user_profile)
    return Response(serializer.data)


class UserProfileView(views.APIView):
    permission_classes = (IsOwner,)

    def get(self, request):
        user_profile = request.user.profile
        self.check_object_permissions(request, user_profile)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def put(self, request):
        user_profile = request.user.profile
        self.check_object_permissions(request, user_profile)
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user_profile = request.user.profile
        self.check_object_permissions(request, user_profile)
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user_profile = request.user.profile
        self.check_object_permissions(request, user_profile)
        user_profile.user.delete()
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAddressView(viewsets.ViewSet):
    permission_classes = (IsOwner,)

    def list(self, request):
        query_set = request.user.profile.addresses
        serializer = UserAddressSerializer(query_set, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, sort=pk, user=request.user.profile)
        serializer = UserAddressSerializer(address)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, sort=pk, user=request.user.profile)
        serializer = UserAddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, sort=pk, user=request.user.profile)
        serializer = UserAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, sort=pk, user=request.user.profile)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
