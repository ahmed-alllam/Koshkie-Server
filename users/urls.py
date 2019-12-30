#  Copyright (c) Code Written and Tested by Ahmed Emad in 30/12/2019, 17:08

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserProfileView, UserAddressView, login_view, logout_view

router = DefaultRouter()
router.register('', UserAddressView, basename='addresses')

app_name = 'users'

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('signup/', UserProfileView.as_view({'post': 'create'})),
    path('me/', UserProfileView.as_view({'get': 'retrieve',
                                         'put': 'update',
                                         'patch': 'partial_update',
                                         'delete': 'destroy'})),
    path('<username>/', UserProfileView.as_view({'get': 'retrieve'})),
    path('addresses/', include(router.urls))
]
