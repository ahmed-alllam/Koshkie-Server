#  Copyright (c) Code Written and Tested by Ahmed Emad in 06/01/2020, 16:28

from abc import ABC

from django.contrib.auth import login
from django.db.models import F, Func
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from shops.models import ShopProfileModel
from shops.permissions import ShopProfilePermissions
from shops.serializers import ShopProfileSerializer, ShopProfileDetailSerializer


class Sin(Func, ABC):
    function = 'SIN'


class Cos(Func, ABC):
    function = 'COS'


class Acos(Func, ABC):
    function = 'ACOS'


class Rad(Func, ABC):
    function = 'RADIANS'


class ShopProfileView(viewsets.ViewSet):
    permission_classes = (ShopProfilePermissions,)

    def list(self, request):
        try:
            user_longitude = float(request.GET.get('longitude'))
            user_latitude = float(request.GET.get('latitude'))
        except Exception:
            return Response("invalid coordinates", status=status.HTTP_400_BAD_REQUEST)

        queryset = ShopProfileModel.objects.annotate(distance=
                                                     6367 * Acos(Cos(Rad(float(user_latitude))) *
                                                                 Cos(Rad(F('address__location_longitude'))) *
                                                                 Cos(Rad(F('address__location_latitude')) -
                                                                     Rad(float(user_longitude))
                                                                     ) +
                                                                 Sin(Rad(float(user_latitude))) *
                                                                 Sin(Rad(F('address__location_latitude')))
                                                                 )
                                                     ).filter(distance__lte=2.5, is_open=True,
                                                              opens_at__lte=timezone.now(),
                                                              closes_at__gte=timezone.now()
                                                              ).order_by('distance')

        serializer = ShopProfileSerializer(queryset[:30], many=True)
        return Response(serializer.data)

    def retrieve(self, request, shop_slug):
        shop_profile = get_object_or_404(ShopProfileModel, slug=shop_slug)
        if request.user == shop_profile.account:
            serializer = ShopProfileDetailSerializer(shop_profile)
        else:
            serializer = ShopProfileDetailSerializer(shop_profile, exclude='account')
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_authenticated:
            serializer = ShopProfileDetailSerializer(data=request.data)
            if serializer.is_valid():
                shop_profile = serializer.save()
                login(request, shop_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, shop_slug):
        shop_profile = get_object_or_404(ShopProfileModel, slug=shop_slug)
        self.check_object_permissions(request, shop_profile)
        serializer = ShopProfileDetailSerializer(shop_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug):
        shop_profile = get_object_or_404(ShopProfileModel, slug=shop_slug)
        self.check_object_permissions(request, shop_profile)
        serializer = ShopProfileDetailSerializer(shop_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug):
        shop_profile = get_object_or_404(ShopProfileModel, slug=shop_slug)
        self.check_object_permissions(request, shop_profile)
        shop_profile.account.delete()
        shop_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopReviewView(viewsets.ViewSet):
    def list(self):
        pass

    def create(self):
        pass

    def retrieve(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class ProductGroupView(viewsets.ViewSet):
    def create(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class ProductView(viewsets.ViewSet):
    def list(self):
        pass

    def create(self):
        pass

    def retrieve(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class OptionGroupView(viewsets.ViewSet):
    def create(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class OptionView(viewsets.ViewSet):
    def create(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class AddonView(viewsets.ViewSet):
    def create(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass


class ProductReviewView(viewsets.ViewSet):
    def list(self):
        pass

    def create(self):
        pass

    def retrieve(self):
        pass

    def update(self):
        pass

    def partially_update(self):
        pass

    def destroy(self):
        pass
