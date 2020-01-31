#  Copyright (c) Code Written and Tested by Ahmed Emad in 31/01/2020, 17:29

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserProfileView, UserAddressView, user_login

addresses_router = DefaultRouter()
addresses_router.register('', UserAddressView, basename='addresses')

app_name = 'users'

urlpatterns = [
    path('signup', UserProfileView.as_view({'post': 'create'}), name='signup'),
    path('login/', user_login, name='login'),
    path('<username>/', UserProfileView.as_view({'get': 'retrieve',
                                                 'put': 'update',
                                                 'patch': 'partial_update',
                                                 'delete': 'destroy'}), name='details'),
    path('<username>/addresses/', include(addresses_router.urls))
]
