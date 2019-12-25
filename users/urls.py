#  Copyright (c) Code Written and Tested by Ahmed Emad on 2019

from rest_framework import routers

from users.views import UserViewSet

router = routers.SimpleRouter()
router.register(r'', UserViewSet)
urlpatterns = router.urls
