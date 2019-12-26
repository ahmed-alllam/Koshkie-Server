#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.urls import path

from users.views import (UserProfileView, UserProfileDetailView,
                         UserAddressView, UserAddressDetailView)

urlpatterns = [
    path('/', UserProfileView.as_view()),  # get, post
    path('<int:id>/', UserProfileDetailView.as_view()),  # get, put, patch, delete
    path('addresses/', UserAddressView.as_view()),  # get, post
    path('addresses/<int:id>', UserAddressDetailView.as_view())  # get, put, patch, delete
]
