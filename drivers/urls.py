#  Copyright (c) Code Written and Tested by Ahmed Emad in 08/01/2020, 12:38
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView

driver_reviews_router = DefaultRouter()
driver_reviews_router.register('', DriverReviewView, 'reviews')

app_name = 'drivers'

urlpatterns = [
    path('', DriverProfileView.as_view({'get': 'list', 'post': 'create'})),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve',
                                                   'put': 'update',
                                                   'patch': 'partial_update',
                                                   'delete': 'destroy'})),
    path('<username>/reviews/', include(driver_reviews_router.urls))
]
