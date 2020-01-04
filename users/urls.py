#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/01/2020, 12:48

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserProfileView, UserAddressView

router = DefaultRouter()
router.register('', UserAddressView, basename='addresses')

app_name = 'users'

urlpatterns = [
    path('signup/', UserProfileView.as_view({'post': 'create'})),
    path('<username>/', UserProfileView.as_view({'get': 'retrieve',
                                                 'put': 'update',
                                                 'patch': 'partial_update',
                                                 'delete': 'destroy'})),
    path('<username>/addresses/', include(router.urls))
]
