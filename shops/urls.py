#  Copyright (c) Code Written and Tested by Ahmed Emad in 08/01/2020, 12:38
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shops.views import (ShopProfileView, ShopReviewView, ProductView, ProductReviewView)

shop_reviews_router = DefaultRouter('')
shop_reviews_router.register('', ShopReviewView, 'shop reviews')

product_reviews_router = DefaultRouter('')
product_reviews_router.register('', ProductReviewView, 'product reviews')

app_name = 'shops'

urlpatterns = [
    path('', ShopProfileView.as_view({'get': 'list', 'post': 'create'})),
    path('<slug:shop_slug>/', ShopProfileView.as_view({'get': 'retrieve',
                                                       'put': 'update',
                                                       'patch': 'partial_update',
                                                       'delete': 'destroy'})),

    path('<slug:shop_slug>/reviews/', include(shop_reviews_router.urls)),
    # path('<slug:shop_slug>/product-groups/', ProductGroupView.as_view()),  # shop admin only

    path('<slug:shop_slug>/products/', ProductView.as_view({'get': 'list', 'post': 'create'})),
    path('<slug:shop_slug>/products/<slug:product_slug>/', ProductView.as_view({'get': 'retrieve',
                                                                                'put': 'update',
                                                                                'patch': 'partial_update',
                                                                                'delete': 'destroy'})),

    path('<slug:shop_slug>/products/<slug:product_slug>/reviews/', include(product_reviews_router.urls)),

    # path('<slug:shop_slug>/products/<slug:product_slug>/option-groups/', OptionGroupView.as_view()),  # shop admin only
    # path('<slug:shop_slug>/products/<slug:product_slug>/option-groups/options/', OptionView),  # shop admin only
    # path('<slug:shop_slug>/products/<slug:product_slug>/addons/', AddonView),  # shop admin only
]
