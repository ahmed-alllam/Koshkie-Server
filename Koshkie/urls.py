#  Copyright (c) Code Written and Tested by Ahmed Emad in 10/01/2020, 18:25
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from koshkie.views import logout_view

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('logout/', logout_view),
                  path('users/', include('users.urls')),
                  path('drivers/', include('drivers.urls')),
                  path('shops/', include('shops.urls')),
                  path('orders/', include('orders.urls'))
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(r'^__debug__/', include(debug_toolbar.urls)),
]
