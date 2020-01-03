#  Copyright (c) Code Written and Tested by Ahmed Emad in 03/01/2020, 19:48
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView

router = DefaultRouter()
router.register('', DriverReviewView, 'reviews')

app_name = 'drivers'

urlpatterns = [
    path('signup/', DriverProfileView.as_view({'post': 'create'})),
    path('', DriverProfileView.as_view({'get': 'list'})),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve',
                                                   'put': 'update',
                                                   'patch': 'partial_update',
                                                   'delete': 'destroy'})),
    path('<username>/reviews/', include(router.urls))
]
