#  Copyright (c) Code Written and Tested by Ahmed Emad in 09/01/2020, 14:45
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shops.views import (ShopProfileView, ShopReviewView, ProductView, ProductReviewView, ProductGroupView, AddOnView,
                         OptionGroupView, OptionView)

shop_reviews_router = DefaultRouter()
shop_reviews_router.register('', ShopReviewView, 'shop reviews')

product_reviews_router = DefaultRouter()
product_reviews_router.register('', ProductReviewView, 'product reviews')

product_group_router = DefaultRouter()
product_group_router.register('', ProductGroupView, 'product group')

option_group_router = DefaultRouter()
option_group_router.register('', OptionGroupView, 'option group')

option_router = DefaultRouter()
option_router.register('', OptionView, 'options')

addon_router = DefaultRouter()
addon_router.register('', AddOnView, 'add-ons')


app_name = 'shops'

urlpatterns = [
    path('', ShopProfileView.as_view({'get': 'list', 'post': 'create'})),
    path('<slug:shop_slug>/', ShopProfileView.as_view({'get': 'retrieve',
                                                       'put': 'update',
                                                       'patch': 'partial_update',
                                                       'delete': 'destroy'})),

    path('<slug:shop_slug>/reviews/', include(shop_reviews_router.urls)),
    path('<slug:shop_slug>/product-groups/', include(product_group_router.urls)),

    path('<slug:shop_slug>/products/', ProductView.as_view({'get': 'list', 'post': 'create'})),
    path('<slug:shop_slug>/products/<slug:product_slug>/', ProductView.as_view({'get': 'retrieve',
                                                                                'put': 'update',
                                                                                'patch': 'partial_update',
                                                                                'delete': 'destroy'})),

    path('<slug:shop_slug>/products/<slug:product_slug>/reviews/', include(product_reviews_router.urls)),
    path('<slug:shop_slug>/products/<slug:product_slug>/option-groups/', include(option_group_router.urls)),
    path('<slug:shop_slug>/products/<slug:product_slug>/option-groups/<int:group_id>/options/',
         include(option_router.urls)),
    path('<slug:shop_slug>/products/<slug:product_slug>/addons/', include(addon_router.urls))
]
