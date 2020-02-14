#  Copyright (c) Code Written and Tested by Ahmed Emad in 14/02/2020, 14:50

from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from orders.models import OrderModel
from orders.permissions import OrderPermissions
from orders.serializers import OrderSerializer, OrderDetailSerializer


class OrderView(viewsets.ViewSet):
    """View for the user profile.

    Lists, Creates and Updates an Order.
    """

    permission_classes = (OrderPermissions,)
    serializer_class = OrderDetailSerializer

    def list(self, request):
        """Lists all orders the user has.

        Arguments:
            request: the request data sent by the user, it is used
                     for Pagination

            Returns:
                HTTP 403 if user is not authenticated
                HTTP 200 Response with all orders in JSON.
        """

        queryset = None

        if hasattr(request.user, 'profile'):
            queryset = request.user.profile.orders.all()  # this is a regular user

        if hasattr(request.user, 'driver_profile'):
            queryset = request.user.driver_profile.served_orders.all()  # this is a driver

        if hasattr(request.user, 'shop_profile'):
            queryset = request.user.shop_profile.served_orders.all()  # this is a shop

        paginator = LimitOffsetPagination()
        paginator.default_limit = 15
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrderSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'orders': serializer.data})

    def retrieve(self, request, pk=None):
        """Retrieves a certain order from the user's list

        Arguments:
            request: the request data sent by the user, it is used
                     to checks the user's permissions
            pk: the sort of the address that the user want info about,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to see that order,
            HTTP 404 Response if order is not found, if not,
            returns HTTP 200 Response with the order's JSON data.
        """

        order = get_object_or_404(OrderModel, pk=pk)
        self.check_object_permissions(request, order)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    def create(self, request):
        """Creates a new order and adds it to the user's list.

        Arguments:
            request: the request data sent by the user, it is used
                     to get the request data

        Returns:
            HTTP 403 Response if the user is
            not authorized to add an order,
            HTTP 400 Response if the data is not valid, if not,
            returns HTTP 201 Response with the order's JSON data.
        """

        serializer = OrderDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """Partially Updates a certain order from the user's list.
        only driver can update the order, there is only one
        field that can be updated which is the order status.

        Arguments:
            request: the request data sent by the user, it is used
                     to check the user's permissions and get the data.
            pk: the id of the order that the user wants to change,
                it should by an integer.

        Returns:
            HTTP 403 Response if the user is
            not authorized to update that order,
            HTTP 400 Response if the data is not valid with the errors,
            HTTP 404 Response if the order is not found
            if not returns HTTP 200 Response with the updated JSON data.
        """

        order = get_object_or_404(OrderModel, pk=pk)
        self.check_object_permissions(request, order)
        serializer = OrderDetailSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
