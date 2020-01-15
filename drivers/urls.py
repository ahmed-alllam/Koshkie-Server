#  Copyright (c) Code Written and Tested by Ahmed Emad in 15/01/2020, 12:16
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView, driver_login

driver_reviews_router = DefaultRouter()
driver_reviews_router.register('', DriverReviewView, 'reviews')

app_name = 'drivers'

urlpatterns = [
    path('', DriverProfileView.as_view({'get': 'list'})),
    path('signup/', DriverProfileView.as_view({'post': 'create'})),
    path('login/', driver_login),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve',
                                                   'put': 'update',
                                                   'patch': 'partial_update',
                                                   'delete': 'destroy'})),
    path('<username>/reviews/', include(driver_reviews_router.urls))
]
