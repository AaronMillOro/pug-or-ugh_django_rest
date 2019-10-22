from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveAPIView, RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
#from rest_framework.views import APIView

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


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
    lookup_field = None

    def get_object(self):
        user = self.request.user
        try:
            user_pref = models.UserPref.objects.get(user_id=user.id)
        except models.UserPref.DoesNotExist:
            user_pref = models.UserPref.objects.create(user=user)
        return user_pref


class ListDogsView(ListAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer


def convert_dog_age(prefered_age):
    """
    Inspection of data range showed a range between  2 and 96 months
    """
    if prefered_age == 'b':
        dog_age = list(range(1,11))
    elif prefered_age == "y":
        dog_age = list(range(11,30))
    elif prefered_age == "a":
        dog_age = list(range(30,70))
    elif prefered_age == "s":
        dog_age = list(range(70,100))
    else:
        print("Invalid code. Try again!")
        dog_age = list(range(1,11))
        # Default value is sent
    return dog_age


class RetrieveUndecided(RetrieveAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        """
        Return the query containing 'undecided' dogs
        Added equivalent tags of age field to UserPref (letter)
        compared to Dog model (integer)
        """
        user_pref = models.UserPref.objects.get(user=self.request.user)
        user_dog_queryset = models.UserDog.objects.filter(user=self.request.user)

        queryset = self.queryset.filter(
            gender__in=preference.gender,
            size__in=preference.size,
        )

        pass

    def get_object(self):
        """ Return a single dog from the filtered queryset(undecided)"""
        pass
