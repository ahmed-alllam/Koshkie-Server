#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/01/2020, 12:48

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from koshkie.views import logout_view, login_view

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('login/', login_view),
                  path('logout/', logout_view),
                  path('users/', include('users.urls')),
                  path('drivers/', include('drivers.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
