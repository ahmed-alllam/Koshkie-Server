#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019
from django.contrib.auth import login
from rest_framework import viewsets, views, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import UserProfileModel, UserAddressModel
from users.serializers import UserProfileSerializer, UserAddressSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        return obj.user.user == request.user


class UserViewPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        return obj.user.user == request.user


class UserProfileView(views.APIView):
    permission_class = UserViewPermission

    def get(self, request, pk=None):
        user_profile = None
        if pk:
            user_profile = get_object_or_404(UserProfileModel, pk=pk)
        else:
            if request.user.is_authenticated:
                user_profile = request.user.profile
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_profile = serializer.save()
            login(request, user_profile.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        user_profile = None
        if pk:
            user_profile = get_object_or_404(UserProfileModel, pk=pk)
        else:
            user_profile = request.user.profile

        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        user_profile = None
        if pk:
            user_profile = get_object_or_404(UserProfileModel, pk=pk)
        else:
            user_profile = request.user.profile

        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        user_profile = None
        if pk:
            user_profile = get_object_or_404(UserProfileModel, pk=pk)
        else:
            user_profile = request.user.profile

        user_profile.user.delete()
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAddressView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, IsOwner)

    def list(self, request):
        query_set = request.user.profile.addresses
        serializer = UserAddressSerializer(query_set, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, pk=pk)
        serializer = UserAddressSerializer(address, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = UserAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, pk=pk)
        serializer = UserAddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        address = get_object_or_404(UserAddressModel, pk=pk)
        serializer = UserAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destory(self, request, pk=None):
        user_address = get_object_or_404(UserAddressModel, pk=pk)
        UserAddressModel.objects.delete(user_address)
        return Response(status=status.HTTP_204_NO_CONTENT)
