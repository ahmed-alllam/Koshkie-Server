#  Copyright (c) Code Written and Tested by Ahmed Emad in 17/01/2020, 21:37
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from drivers.models import DriverProfileModel
from orders.models import OrderModel
from orders.permissions import OrderPermissions
from orders.serializers import OrderSerializer, OrderDetailSerializer


class OrderView(viewsets.ViewSet):
    permission_classes = (OrderPermissions,)

    def list(self, request):
        queryset = None

        if hasattr(request.user, 'profile'):
            queryset = request.user.profile.orders.all()

        if hasattr(request.user, 'driver_profile'):
            queryset = request.user.driver_profile.served_orders.all()

        if hasattr(request.user, 'shop_profile'):
            queryset = request.user.shop_profile.served_orders.all()

        paginator = LimitOffsetPagination()
        paginator.default_limit = 15
        paginator.max_limit = 100
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = OrderSerializer(paginated_queryset, many=True)

        return Response(data={'limit': paginator.limit, 'offset': paginator.offset,
                              'count': paginator.count, 'orders': serializer.data})

    def retrieve(self, request, pk=None):
        order = get_object_or_404(OrderModel, pk=pk)
        self.check_object_permissions(request, order)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

    def create(self, request):
        serializer = OrderDetailSerializer(data=request.data)
        if serializer.is_valid():
            driver = DriverProfileModel.objects.get(pk=1)
            serializer.save(user=request.user.profile, driver=driver)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        order = get_object_or_404(OrderModel, pk=pk)
        if order.driver == request.user.driver_profile:  # only the driver can update order arrived status
            serializer = OrderDetailSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
