#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 14:19
from django.contrib.auth import login, authenticate, update_session_auth_hash
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from users.models import UserAddressModel, UserProfileModel
from users.permissions import UserProfilePermissions, UserAddressPermissions
from users.serializers import UserProfileSerializer, UserAddressSerializer


@api_view(['POST'])
def user_login(request):
    """View for logging the users in"""

    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_401_UNAUTHORIZED)

    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user and hasattr(user, 'profile'):
        login(request, user)
        return Response('Logged In Successfully')
    else:
        return Response('Wrong Username or Password', status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(viewsets.ViewSet):
    """View for the user profile.

    Retrieves, Updates and Deletes a User Profile.
    """

    permission_classes = (UserProfilePermissions,)
    serializer_class = UserProfileSerializer

    def retrieve(self, request, username=None):
        """Retrieves a user profile by its username

        Checks if a user profile with this username exist,
        if not, returns HTTP 404 Response.
        requires no permissions.

        Arguments:
            request: the request data sent by the user,
                     it is not used here but required by django
            username: the username of the user profile that the user wants info about.

        Returns:
            HTTP 404 Response if user profile is not found,
            HTTP 403 if user isn't logged in,
            if not, returns HTTP 200 Response with the profile's JSON data.
        """
        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        serializer = self.serializer_class(user_profile)
        return Response(serializer.data)

    def create(self, request):
        """Creates A new user profile and Logs it In.

        Checks if user is authenticated if true, return HTTP 401 Response,
        then it Validates the post data if not valid,
        return HTTP 400 Response, then creates the user and logs him in,
        and returns 201 Response.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the post data from it to get validated and created,
                     and to log the user in.

        Returns:
             HTTP 400 Response if data is not valid,
             HTTP 401 Response if user is already logged in,
             HTTP 201 Response with the JSON data of the created profile.
        """

        if not request.user.is_authenticated:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user_profile = serializer.save()
                login(request, user_profile.account)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, username=None):
        """Completely Updates the user profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile that will be updated

        Returns:
             HTTP 400 Response if the data is not
             valid with the errors,
             HTTP 403 Response if the user is not
             authorized to update that profile
             if not returns HTTP 200 Response with the update JSON data.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        serializer = self.serializer_class(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, user_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None):
        """Partially Updates the user profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile and the post data.
            username: the username of the user profile that will be updated

        Returns:
             HTTP 400 Response if the data is not valid with the errors,
             HTTP 403 Response if the user is not
             authorized to update that profile,
             if not returns HTTP 200 Response with the update JSON data.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        serializer = self.serializer_class(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            update_session_auth_hash(request, user_profile.account)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None):
        """Deletes the user profile.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile that will be deleted

        Returns:
            HTTP 404 Response if user profile is not found
            HTTP 403 Response if the user is not authorized
            to update that profile,
            if not returns HTTP 204 Response with no content.
        """

        user_profile = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user_profile)
        user_profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAddressView(viewsets.ViewSet):
    """View for the user addresses.

    Lists, Creates, Updates and Deletes an Address, requires user authentication.
    """

    permission_classes = (UserAddressPermissions,)
    serializer_class = UserAddressSerializer

    def list(self, request, username=None):
        """Lists all addresses the user has.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      whose addresses will be returned

        Returns:
            HTTP 403 Response if the user is
            not authorized to see that user's addresses,
            HTTP 404 if user profile is not found,
            HTTP 200 Response with all addresses in
            the user's profile in JSON.
        """

        user = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user)
        queryset = user.addresses.all()

        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'addresses': serializer.data})

    def retrieve(self, request, username=None, pk=None):
        """Retrieves a certain address from the user's list

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      whose address will be returned
            pk: the sort of the address that the user want info about,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to see that user's address,
            HTTP 404 Response if address is not found, if not,
            returns HTTP 200 Response with the address's JSON data.
        """
        address = get_object_or_404(UserAddressModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, address)
        serializer = self.serializer_class(address)
        return Response(serializer.data)

    def create(self, request, username=None):
        """Creates a new address and adds it to the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      which will be added a new address

        Returns:
            HTTP 403 Response if the user is
            not authorized to add an address to that user,
            HTTP 404 if user profile is not found,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the address's JSON data.
        """
        user = get_object_or_404(UserProfileModel, account__username=username)
        self.check_object_permissions(request, user)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(username=username)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, username=None, pk=None):
        """Completely Updates a certain address from the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      whose address will be updated
            pk: the id of the address that the user wants to change,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to update an address to that user,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the address is not found
            if not returns HTTP 200 Response with the update JSON data.
        """
        address = get_object_or_404(UserAddressModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, address)
        serializer = self.serializer_class(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, username=None, pk=None):
        """Partially Updates a certain address from the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      whose address will be updated
            pk: the id of the address that the user wants to change,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to update an address to that user,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the address is not found
            if not returns HTTP 200 Response with the update JSON data.
        """
        address = get_object_or_404(UserAddressModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, address)
        serializer = self.serializer_class(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, username=None, pk=None):
        """Deletes a certain address from the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the user profile.
            username: the username of the user profile
                      whose address will be deleted
            pk: the id of the address that the user wants to delete,
                it should by an integer.
        Returns:
            HTTP 404 Response if the address is not found
            HTTP 403 Response if the user is
            not authorized to delete an address to that user,
            if not, returns HTTP 204 Response with no content.
        """
        address = get_object_or_404(UserAddressModel, sort=pk, user__account__username=username)
        self.check_object_permissions(request, address)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
