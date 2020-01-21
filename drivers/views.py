#  Copyright (c) Code Written and Tested by Ahmed Emad in 21/01/2020, 15:27
from abc import ABC

from django.contrib.auth import login, authenticate
from django.db.models import Func, F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from drivers.models import DriverProfileModel, DriverReviewModel
from drivers.permissions import DriverProfilePermissions, DriverReviewPermissions
from drivers.serializers import DriverProfileSerializer, DriverReviewSerializer


class Sin(Func, ABC):
    function = 'SIN'


class Cos(Func, ABC):
    function = 'COS'


class Acos(Func, ABC):
    function = 'ACOS'


class Rad(Func, ABC):
    function = 'RADIANS'


@api_view(['POST'])
def driver_login(request):
    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_401_UNAUTHORIZED)

    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user and hasattr(user, 'driver_profile'):
        login(request, user)
        return Response('Logged In Successfully')
    else:
        return Response('Wrong Username or Password', status=status.HTTP_400_BAD_REQUEST)


class DriverProfileView(viewsets.ViewSet):
    permission_classes = (DriverProfilePermissions,)
    serializer_class = DriverProfileSerializer

    def list(self, request):
        try:
            user_longitude = float(request.GET.get('longitude'))
            user_latitude = float(request.GET.get('latitude'))
        except Exception:
            return Response("invalid coordinates", status=status.HTTP_400_BAD_REQUEST)

        min_active_time = timezone.now() - timezone.timedelta(seconds=10)
        queryset = DriverProfileModel.objects.annotate(distance=
                                                       6367 * Acos(Cos(Rad(float(user_latitude))) *
                                                                   Cos(Rad(F('live_location_longitude'))) *
                                                                   Cos(Rad(F('live_location_latitude')) -
                                                                       Rad(float(user_longitude))
                                                                       ) +
                                                                   Sin(Rad(float(user_latitude))) *
                                                                   Sin(Rad(F('live_location_latitude')))
                                                                   )
                                                       ).filter(distance__lte=2.5, is_busy=False,
                                                                last_time_online__gte=min_active_time
                                                                ).order_by('distance')

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = DriverProfileSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'drivers': serializer.data})

    def retrieve(self, request, username=None):
        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        serializer = DriverProfileSerializer(driver_profile)
        return Response(serializer.data)

    def create(self, request):
        if not request.user.is_authenticated:
            serializer = DriverProfileSerializer(data=request.data)
            if serializer.is_valid():
                driver_profile = serializer.save()
                login(request, driver_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, username=None):
        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        serializer = DriverProfileSerializer(driver_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None):
        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        serializer = DriverProfileSerializer(driver_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None):
        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        driver_profile.account.delete()
        driver_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverReviewView(viewsets.ViewSet):
    permission_classes = (DriverReviewPermissions,)
    serializer_class = DriverReviewSerializer

    def list(self, request, username=None):
        queryset = DriverReviewModel.objects.filter(driver__account__username=username).all()
        paginator = LimitOffsetPagination()
        paginator.default_limit = 25
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = DriverReviewSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'reviews': serializer.data})

    def retrieve(self, request, username=None, pk=None):
        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        serializer = DriverReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request, username=None):
        driver = get_object_or_404(DriverProfileModel, account__username=username)
        serializer = DriverReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile, driver=driver)
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
        driver = review.driver
        review.delete()

        driver.calculate_rating()
        driver.resort_reviews(review.sort)
        driver.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
