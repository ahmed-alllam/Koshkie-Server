#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/12/2019, 20:06
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from drivers.views import DriverProfileView, DriverReviewView, login_view, logout_view

router = DefaultRouter()
router.register('', DriverReviewView, 'reviews')

app_name = 'drivers'

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('signup/', DriverProfileView.as_view({'post': 'create'})),
    path('', DriverProfileView.as_view({'get': 'list'})),
    path('me/', DriverProfileView.as_view({'get': 'retrieve',
                                           'put': 'update',
                                           'patch': 'partial_update',
                                           'delete': 'destroy'})),
    path('<username>/', DriverProfileView.as_view({'get': 'retrieve'})),
    path('<username>/reviews/', include(router.urls))
]
