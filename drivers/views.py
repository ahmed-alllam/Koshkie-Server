#  Copyright (c) Code Written and Tested by Ahmed Emad in 30/12/2019, 17:08
from django.contrib.auth import login
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from drivers.models import DriverProfileModel, DriverReviewModel
from drivers.permissions import DriverProfilePermissions, DriverReviewPermissions
from drivers.serializers import DriverProfileSerializer, DriverReviewSerializer


class DriverProfileView(viewsets.ViewSet):
    permission_classes = (DriverProfilePermissions,)

    def list(self, request):
        return Response()

    def retrieve(self, request, username=None):
        if username:
            driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
            serializer = DriverProfileSerializer(driver_profile)
            return Response(serializer.data)
        if request.user.is_authenticated and hasattr(request.user, 'driver_profile'):
            driver_profile = request.user.driver_profile
            serializer = DriverProfileSerializer(driver_profile)
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request):
        if not request.user.is_authenticated:
            serializer = DriverProfileSerializer(data=request.data)
            if serializer.is_valid():
                driver_profile = serializer.save()
                login(request, driver_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request):
        driver_profile = request.user.driver_profile
        serializer = DriverProfileSerializer(driver_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request):
        driver_profile = request.user.driver_profile
        serializer = DriverProfileSerializer(driver_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request):
        driver_profile = request.user.driver_profile
        driver_profile.account.delete()
        driver_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverReviewView(viewsets.ViewSet):
    permission_classes = (DriverReviewPermissions,)

    def list(self, username=None):
        query_set = DriverProfileModel.objects.filter(account__username=username).reviews.all()
        serializer = DriverReviewSerializer(query_set, many=True)
        return Response(serializer.data)

    def retrieve(self, request, username=None, pk=None):
        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        serializer = DriverReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request, username=None):
        serializer = DriverReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile, driver__account__username=username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, pk=None):
        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        serializer = DriverReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None, pk=None):
        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        serializer = DriverReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, pk=None):
        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
