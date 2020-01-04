#  Copyright (c) Code Written and Tested by Ahmed Emad in 04/01/2020, 12:48
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def login_view(request):
    if request.user.is_authenticated:
        return Response('User already logged in', status=status.HTTP_401_UNAUTHORIZED)

    username = request.data['username']
    password = request.data['password']

    user = authenticate(username=username, password=password)

    if user:
        login(request, user)
        return Response('Logged In Successfully')
    else:
        return Response('Wrong Username or Password', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
def logout_view(request):
    logout(request)
    return Response('Logged Out Successfully')
