#  Copyright (c) Code Written and Tested by Ahmed Emad in 10/01/2020, 18:25

from rest_framework import viewsets

from orders.permissions import OrderPermissions


class OrderView(viewsets.ViewSet):
    permission_classes = (OrderPermissions,)

    def list(self, request):
        pass

    def retrieve(self, request):
        pass

    def create(self, request):
        pass

    def update(self, request):
        pass

    def partial_update(self, request):
        pass

    def destroy(self, request):
        pass
