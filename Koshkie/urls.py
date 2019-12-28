#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from koshkie.views import login_view, logout_view

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('users/', include('users.urls')),
                  path('login', login_view),
                  path('logout', logout_view)
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
