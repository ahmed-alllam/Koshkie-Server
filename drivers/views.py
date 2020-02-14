#  Copyright (c) Code Written and Tested by Ahmed Emad in 14/02/2020, 14:50

from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from drivers.models import DriverProfileModel, DriverReviewModel
from drivers.permissions import DriverProfilePermissions, DriverReviewPermissions
from drivers.serializers import DriverProfileSerializer, DriverReviewSerializer
from koshkie import haversine


@api_view(['POST'])
def driver_login(request):
    """View for logging the drivers in"""

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
    """View for the driver profile.

    Lists, Retrieves, Updates and Deletes a driver Profile.
    """
    permission_classes = (DriverProfilePermissions,)
    serializer_class = DriverProfileSerializer

    def list(self, request):
        """Lists all available driver profiles near a certain location

        Arguments:
            request: the request data sent by the user,
                     it is used to get the queries entered by user,
                     and for Pagination

        Returns:
            returns HTTP 200 Response with the drivers' JSON data.
            if there are no coordinates given will return 400 Response.
        """

        try:
            user_longitude = float(request.GET.get('longitude'))
            user_latitude = float(request.GET.get('latitude'))
        except Exception:
            return Response("invalid coordinates", status=status.HTTP_400_BAD_REQUEST)

        min_active_time = timezone.now() - timezone.timedelta(seconds=10)
        queryset = DriverProfileModel.objects.annotate(distance=haversine(user_latitude, user_longitude,
                                                                          F('live_location_latitude'),
                                                                          F('live_location_longitude'))
                                                       ).filter(distance__lte=2.5, is_busy=False,
                                                                last_time_online__gte=min_active_time,
                                                                is_active=True, is_available=True
                                                                ).order_by('distance')

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = DriverProfileSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'drivers': serializer.data})

    def retrieve(self, request, username=None):
        """Retrieves a driver profile by its username

        Checks if a driver profile with this username exist,
        if not, returns HTTP 404 Response.

        Arguments:
            request: the request data sent by the user,
                     it is not used here but required by django
            username: the username of the driver profile that the user wants info about.

        Returns:
            HTTP 404 Response if driver profile is not found,
            if not, returns HTTP 200 Response with the profile's JSON data.
        """

        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        serializer = DriverProfileSerializer(driver_profile)
        return Response(serializer.data)

    def create(self, request):
        """Creates A new driver profile and Logs it In.

        Checks if user is authenticated if true, return HTTP 401 Response,
        then it Validates the post data if not valid,
        return HTTP 400 Response, then creates the driver and logs him in,
        and returns 201 Response.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the post data from it to get validated and created,
                     and to log the driver in.

        Returns:
            HTTP 400 Response if data is not valid,
            HTTP 401 Response if user is already logged in,
            HTTP 201 Response with the JSON data of the created profile.
        """

        if not request.user.is_authenticated:
            serializer = DriverProfileSerializer(data=request.data)
            if serializer.is_valid():
                driver_profile = serializer.save()
                login(request, driver_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, username=None):
        """Completely Updates the driver profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the driver profile that will be updated

        Returns:
            HTTP 404 Response if driver profile is not found,
            HTTP 400 Response if the data is not
            valid with the errors,
            HTTP 403 Response if the user is not
            authorized to update that profile
            if not returns HTTP 200 Response with the update JSON data.
        """

        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        serializer = DriverProfileSerializer(driver_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, driver_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None):
        """Partially Updates the driver profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the driver profile that will be updated

        Returns:
            HTTP 404 Response if driver profile is not found,
            HTTP 400 Response if the data is
            not valid with the errors,
            HTTP 403 Response if the user is not
            authorized to update that profile,
            if not returns HTTP 200 Response with the update JSON data.
        """

        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        serializer = DriverProfileSerializer(driver_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, driver_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None):
        """Deletes the driver profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the driver profile that will be deleted

        Returns:
            HTTP 404 Response if driver profile is not found
            HTTP 403 Response if the user is not authorized
            to update that profile,
            if not returns HTTP 204 Response with no content.
        """
        driver_profile = get_object_or_404(DriverProfileModel, account__username=username)
        self.check_object_permissions(request, driver_profile)
        driver_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DriverReviewView(viewsets.ViewSet):
    """View for the driver reviews.

    Lists, Creates, Updates and Deletes a driver review
    """

    permission_classes = (DriverReviewPermissions,)
    serializer_class = DriverReviewSerializer

    def list(self, request, username=None):
        """Lists all reviews the driver has.

        Arguments:
            request: the request data sent by the user, it is
                     used for Pagination
            username: the username of the driver profile
                      whose reviews will be returned

        Returns:
            HTTP 404 if driver profile is not found,
            HTTP 200 Response with all reviews in
            the driver's profile in JSON.
        """

        driver = get_object_or_404(DriverProfileModel, account__username=username)
        queryset = driver.reviews.all()
        paginator = LimitOffsetPagination()
        paginator.default_limit = 25
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = DriverReviewSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'reviews': serializer.data})

    def retrieve(self, request, username=None, pk=None):
        """Retrieves a certain review from the driver's reviews

        Arguments:
            request: the request data sent by the user, it is not used
                     here but required by django

            username: the username of the driver profile
                      whose review will be returned

            pk: the sort of the review that the user want info about,
                it should by an integer.

        Returns:
            HTTP 404 Response if review or driver are not found, if not,
            returns HTTP 200 Response with the address's JSON data.
        """

        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        serializer = DriverReviewSerializer(review)
        return Response(serializer.data)

    def create(self, request, username=None):
        """Creates a new review and adds it to the driver's reviews.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the driver profile
                      which will be added a new review

        Returns:
            HTTP 403 Response if the user is
            not authorized to add a review to that driver,
            HTTP 404 if driver profile is not found,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the review's JSON data.
        """

        driver = get_object_or_404(DriverProfileModel, account__username=username)
        serializer = DriverReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile, driver=driver)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, pk=None):
        """Completely Updates a certain review from the driver's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the driver profile
                      whose review will be updated
            pk: the id of the review that the user wants to change,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to update that review,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the review is not found
            if not returns HTTP 200 Response with the update JSON data.
        """

        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        serializer = DriverReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None, pk=None):
        """Partially Updates a certain review from the driver's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data
            username: the username of the driver profile
                      whose review will be updated
            pk: the id of the review that the user wants to change,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to update that review,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the review is not found
            if not returns HTTP 200 Response with the update JSON data.
        """

        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        serializer = DriverReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, pk=None):
        """Deletes a certain review from the driver's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions
            username: the username of the driver profile
                      whose review will be deleted
            pk: the id of the review that the user wants to delete,
                it should by an integer.
        Returns:
            HTTP 404 Response if the address is not found
            HTTP 403 Response if the user is
            not authorized to delete that review,
            if not, returns HTTP 204 Response with no content.
        """

        review = get_object_or_404(DriverReviewModel, driver__account__username=username, sort=pk)
        self.check_object_permissions(request, review)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
