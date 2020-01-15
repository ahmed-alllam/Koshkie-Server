#  Copyright (c) Code Written and Tested by Ahmed Emad in 15/01/2020, 12:16

from abc import ABC

from django.contrib.auth import login, authenticate
from django.db.models import F, Func
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from shops.models import ShopProfileModel, ShopReviewModel, ProductGroupModel, ProductModel, ProductReviewModel, \
    AddOnModel, OptionGroupModel, OptionModel
from shops.permissions import ShopProfilePermissions, ShopReviewPermissions, ProductPermissions, \
    ProductReviewPermissions, ProductGroupPermissions, AddOnPermission, OptionGroupPermissions, OptionPermissions
from shops.serializers import (ShopProfileSerializer, ShopProfileDetailSerializer, ShopReviewSerializer,
                               ProductGroupSerializer, ProductDetailsSerializer, ProductReviewSerializer,
                               AddOnSerializer, OptionGroupSerializer, OptionSerializer, ProductSerializer)


class Sin(Func, ABC):
    function = 'SIN'


class Cos(Func, ABC):
    function = 'COS'


class Acos(Func, ABC):
    function = 'ACOS'


class Rad(Func, ABC):
    function = 'RADIANS'


@api_view(['POST'])
def shop_login(request):
    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_401_UNAUTHORIZED)

    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user and hasattr(user, 'shop_profile'):
        login(request, user)
        return Response('Logged In Successfully')
    else:
        return Response('Wrong Username or Password', status=status.HTTP_400_BAD_REQUEST)


class ShopProfileView(viewsets.ViewSet):
    permission_classes = (ShopProfilePermissions,)

    def list(self, request):
        try:
            user_longitude = float(request.GET.get('longitude'))
            user_latitude = float(request.GET.get('latitude'))
            shop_type = request.GET.get('type')
            search = request.GET.get('search')
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

                                                              ).order_by('distance')
        if shop_type:
            queryset = queryset.filter(shop_type__iexact=shop_type)
        if search:
            queryset = queryset.filter(name__icontains=search)

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

    def partial_update(self, request, shop_slug=None, pk=None):
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
        product_group.shop.resort_product_groups(product_group.sort)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductView(viewsets.ViewSet):
    permission_classes = (ProductPermissions,)

    def list(self, request, shop_slug=None):
        queryset = ProductGroupModel.objects.filter(shop__slug=shop_slug)
        best_selling_queryset = ProductModel.objects.filter(shop__slug=shop_slug,
                                                            num_sold__gt=0).order_by('num_sold')
        best_selling_serializer = ProductSerializer(best_selling_queryset[:5], many=True)

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductGroupSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'best_selling': best_selling_serializer.data,
                              'groups': serializer.data})

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
    permission_classes = (OptionGroupPermissions,)

    def create(self, request, shop_slug=None, product_slug=None):
        product = get_object_or_404(ProductModel, shop__slug=shop_slug, slug=product_slug)
        self.check_object_permissions(request, product)
        serializer = OptionGroupSerializer(data=request.data, context={'product': product})
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, product_slug=None, pk=None):
        product = get_object_or_404(ProductModel, slug=product_slug, shop__slug=shop_slug)
        option_group = get_object_or_404(OptionGroupModel, product=product, sort=pk)
        self.check_object_permissions(request, option_group)
        serializer = OptionGroupSerializer(option_group, data=request.data, context={'product': product})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug=None, product_slug=None, pk=None):
        product = get_object_or_404(ProductModel, slug=product_slug, shop__slug=shop_slug)
        option_group = get_object_or_404(OptionGroupModel, product=product, sort=pk)
        self.check_object_permissions(request, option_group)
        serializer = OptionGroupSerializer(option_group, data=request.data, context={'product': product}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, product_slug=None, pk=None):
        option_group = get_object_or_404(OptionGroupModel, product__slug=product_slug,
                                         product__shop__slug=shop_slug, sort=pk)
        self.check_object_permissions(request, option_group)
        option_group.delete()
        option_group.product.resort_option_groups(option_group.sort)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OptionView(viewsets.ViewSet):
    permission_classes = (OptionPermissions,)

    def create(self, request, shop_slug=None, product_slug=None, group_id=None):
        option_group = get_object_or_404(OptionGroupModel, product__shop__slug=shop_slug,
                                         product__slug=product_slug, sort=group_id)
        self.check_object_permissions(request, option_group)
        serializer = OptionSerializer(data=request.data, context={'option_group': option_group})
        if serializer.is_valid():
            serializer.save(option_group=option_group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, shop_slug=None, product_slug=None, group_id=None, pk=None):
        option_group = get_object_or_404(OptionGroupModel, product__slug=product_slug,
                                         product__shop__slug=shop_slug, sort=group_id)
        option = get_object_or_404(OptionModel, option_group=option_group, sort=pk)
        self.check_object_permissions(request, option)
        serializer = OptionSerializer(option, data=request.data,
                                      context={'option_group': option_group})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, shop_slug=None, product_slug=None, group_id=None, pk=None):
        option_group = get_object_or_404(OptionGroupModel, product__slug=product_slug,
                                         product__shop__slug=shop_slug, sort=group_id)
        option = get_object_or_404(OptionModel, option_group=option_group, sort=pk)
        self.check_object_permissions(request, option)
        serializer = OptionSerializer(option, data=request.data,
                                      context={'option_group': option_group}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, shop_slug=None, product_slug=None, group_id=None, pk=None):
        option = get_object_or_404(OptionModel, option_group__product__slug=product_slug,
                                   option_group__product__shop__slug=shop_slug,
                                   option_group__sort=group_id, sort=pk)
        self.check_object_permissions(request, option)
        option.delete()
        option.option_group.resort_options(option.sort)
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    def partial_update(self, request, shop_slug=None, product_slug=None, pk=None):
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
        addon.delete()
        addon.product.resort_addons(addon.sort)
        return Response(status=status.HTTP_204_NO_CONTENT)
