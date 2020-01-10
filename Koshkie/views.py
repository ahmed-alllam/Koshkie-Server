#  Copyright (c) Code Written and Tested by Ahmed Emad in 10/01/2020, 18:25
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response('Logged Out Successfully')
    return Response('Your are not logged in', status=status.HTTP_401_UNAUTHORIZED)
