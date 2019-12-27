#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (UserProfileView,
                         UserAddressView, my_profile_view)

router = DefaultRouter()
router.register('', UserAddressView)

urlpatterns = [
    path('', UserProfileView.as_view()),  # post
    path('<int:pk>/', UserProfileView.as_view()),  # get, put, patch, delete
    path('me/', my_profile_view),
    path('addresses/', include(router.urls))
]
