#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (UserProfileView,
                         UserAddressView, create_user_profile, get_user_profile)

router = DefaultRouter()
router.register('', UserAddressView, basename='UserAddress')

urlpatterns = [
    path('register/', create_user_profile),  # post    any permissions
    path('<int:pk>/', get_user_profile),  # get     any permissions
    path('me/', UserProfileView.as_view()),  # put patch get delete      owner
    path('addresses/', include(router.urls))  # owner
]
