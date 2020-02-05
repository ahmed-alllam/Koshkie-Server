#  Copyright (c) Code Written and Tested by Ahmed Emad in 05/02/2020, 20:26
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView, driver_login

driver_reviews_router = DefaultRouter()
driver_reviews_router.register('', DriverReviewView, basename='reviews')

app_name = 'drivers'

urlpatterns = [
    path('', DriverProfileView.as_view({'get': 'list'}), name='list'),
    path('signup/', DriverProfileView.as_view({'post': 'create'}), name='signup'),
    path('login/', driver_login, name='login'),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve',
                                                   'put': 'update',
                                                   'patch': 'partial_update',
                                                   'delete': 'destroy'}), name='details'),
    path('<username>/reviews/', include(driver_reviews_router.urls))
]
