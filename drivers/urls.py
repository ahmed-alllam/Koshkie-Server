#  Copyright (c) Code Written and Tested by Ahmed Emad in 30/12/2019, 17:08
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView

router = DefaultRouter()
router.register('', DriverReviewView, 'reviews')

app_name = 'drivers'

urlpatterns = [
    path('', DriverProfileView.as_view({'get': 'list', 'post': 'create'})),
    path('me/', DriverProfileView.as_view({'get': 'retrieve',
                                           'put': 'update',
                                           'patch': 'partial_update',
                                           'delete': 'destroy'})),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve'})),
    path('<username>/reviews/', include(router.urls))
]
