#  Copyright (c) Code Written and Tested by Ahmed Emad in 28/12/2019, 22:43

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (UserProfileView,
                         UserAddressView, create_user_profile, get_user_profile)

router = DefaultRouter()
router.register('', UserAddressView, basename='UserAddress')

app_name = 'users'

urlpatterns = [
    path('register/', create_user_profile),
    path('<int:pk>/', get_user_profile),
    path('me/', UserProfileView.as_view()),
    path('addresses/', include(router.urls))
]
