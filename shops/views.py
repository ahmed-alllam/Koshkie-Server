#  Copyright (c) Code Written and Tested by Ahmed Emad in 08/01/2020, 21:55

from abc import ABC

from django.contrib.auth import login
from django.db.models import F, Func
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from shops.models import ShopProfileModel, ShopReviewModel, ProductGroupModel, ProductModel, ProductReviewModel, \
    AddOnModel
from shops.permissions import ShopProfilePermissions, ShopReviewPermissions, ProductPermissions, \
    ProductReviewPermissions, ProductGroupPermissions, AddOnPermission
from shops.serializers import (ShopProfileSerializer, ShopProfileDetailSerializer, ShopReviewSerializer,
                               ProductGroupSerializer, ProductDetailsSerializer, ProductReviewSerializer,
                               AddOnSerializer)


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
            shop_type = request.GET.get('type')
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
        if shop_type:
            queryset = queryset.filter(shop_type__iexact=shop_type)

        paginator = LimitOffsetPagination()
        paginator.default_limit = 25
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ShopProfileSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'shops': serializer.data})

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
    permission_classes = (ShopReviewPermissions,)

    def list(self, request, shop_slug=None):
        queryset = ShopReviewModel.objects.filter(shop__slug=shop_slug).all()

        paginator = LimitOffsetPagination()
        paginator.default_limit = 25
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ShopReviewSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'reviews': serializer.data})

    def retrieve(self, request, shop_slug=None, pk=None):
        review = get_object_or_404(ShopReviewModel, shop__slug=shop_slug, sort=pk)
        serializer = ShopReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request, shop_slug=None):
        shop = get_object_or_404(ShopProfileModel, slug=shop_slug)
        serializer = ShopReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile, shop=shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, pk=None):
        review = get_object_or_404(ShopReviewModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, review)
        serializer = ShopReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug=None, pk=None):
        review = get_object_or_404(ShopReviewModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, review)
        serializer = ShopReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, pk=None):
        review = get_object_or_404(ShopReviewModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, review)
        shop = review.shop
        review.delete()

        shop.calculate_rating()
        shop.resort_reviews(review.sort)
        shop.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductGroupView(viewsets.ViewSet):
    permission_classes = (ProductGroupPermissions,)

    def create(self, request, shop_slug=None):
        shop = get_object_or_404(ShopProfileModel, slug=shop_slug)
        self.check_object_permissions(request, shop)
        serializer = ProductGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, pk=None):
        product_group = get_object_or_404(ProductGroupModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, product_group)
        serializer = ProductGroupSerializer(product_group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partially_update(self, request, shop_slug=None, pk=None):
        product_group = get_object_or_404(ProductGroupModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, product_group)
        serializer = ProductGroupSerializer(product_group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, pk=None):
        product_group = get_object_or_404(ProductGroupModel, shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, product_group)
        product_group.delete()
        product_group.shop.resort_product_groups()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductView(viewsets.ViewSet):
    permission_classes = (ProductPermissions,)

    def list(self, request, shop_slug=None):
        queryset = ProductGroupModel.objects.filter(shop__slug=shop_slug)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductGroupSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'groups': serializer.data})

    def retrieve(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        serializer = ProductDetailsSerializer(product)
        return Response(serializer.data)

    def create(self, request, shop_slug=None):
        shop = get_object_or_404(ShopProfileModel, slug=shop_slug)
        serializer = ProductDetailsSerializer(data=request.data)
        if serializer.is_valid():
            self.check_object_permissions(request, shop)
            product_group = get_object_or_404(ProductGroupModel,
                                              sort=serializer.validated_data.pop('group_id'),
                                              shop__slug=shop_slug)
            serializer.save(shop=shop, product_group=product_group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        self.check_object_permissions(request, product)
        serializer = ProductDetailsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        self.check_object_permissions(request, product)
        serializer = ProductDetailsSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, slug=product_slug, shop__slug=shop_slug)
        self.check_object_permissions(request, product)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewView(viewsets.ViewSet):
    permission_classes = (ProductReviewPermissions,)

    def list(self, request, shop_slug=None, product_slug=None):
        queryset = ProductReviewModel.objects.filter(product__shop__slug=shop_slug,
                                                     product__slug=product_slug).all()
        paginator = LimitOffsetPagination()
        paginator.default_limit = 25
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductReviewSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'reviews': serializer.data})

    def retrieve(self, request, shop_slug=None, product_slug=None, pk=None):
        review = get_object_or_404(ProductReviewModel, product__shop__slug=shop_slug,
                                   product__slug=product_slug, sort=pk)
        serializer = ProductReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, product_slug=None, pk=None):
        review = get_object_or_404(ProductReviewModel, product__shop__slug=shop_slug,
                                   product__slug=product_slug, sort=pk)
        self.check_object_permissions(request, review)
        serializer = ProductReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug=None, product_slug=None, pk=None):
        review = get_object_or_404(ProductReviewModel, product__shop__slug=shop_slug,
                                   product__slug=product_slug, sort=pk)
        self.check_object_permissions(request, review)
        serializer = ProductReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, product_slug=None, pk=None):
        review = get_object_or_404(ProductReviewModel, product__shop__slug=shop_slug,
                                   product__slug=product_slug, sort=pk)
        self.check_object_permissions(request, review)
        product = review.product
        review.delete()

        product.calculate_rating()
        product.resort_reviews(review.sort)
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class AddOnView(viewsets.ViewSet):
    permission_classes = (AddOnPermission,)

    def create(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        self.check_object_permissions(request, product)
        serializer = AddOnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, product_slug=None, pk=None):
        addon = get_object_or_404(AddOnModel, product__slug=product_slug,
                                  product__shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, addon)
        serializer = AddOnSerializer(addon, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partially_update(self, request, shop_slug=None, product_slug=None, pk=None):
        addon = get_object_or_404(AddOnModel, product__slug=product_slug,
                                  product__shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, addon)
        serializer = AddOnSerializer(addon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, product_slug=None, pk=None):
        addon = get_object_or_404(AddOnModel, product__slug=product_slug,
                                  product__shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, addon)
        addon.product.resort_addons()
        return Response(status=status.HTTP_204_NO_CONTENT)
