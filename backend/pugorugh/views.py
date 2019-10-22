from django.contrib.auth import get_user_model
#from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
#from rest_framework.views import APIView

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class ListDogsView(ListAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


class UserPrefView(RetrieveUpdateAPIView):
    """
    User preferences allowing to do GET, POST and PUT
    Available options are in parenthesis, choose at least one of each category:
    age : Baby(b), Young(y), Adult(a) and Senior(s)
    gender : Male(m) and Female(f)
    size : Small(s), Medium(m), Large(l) and Extra large(xl)
    """
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    
