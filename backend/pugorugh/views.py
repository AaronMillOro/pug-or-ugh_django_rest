from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import mixins, permissions, status, viewsets
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


# api/user/preferences/
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
            user_pref = models.UserPref.objects.get(user=user.id)
        except models.UserPref.DoesNotExist:
            user_pref = models.UserPref.objects.create(user=user)
        return user_pref


#/api/dogs/
class ListDogsView(ListAPIView):
    """
    View to inspect all the dogs present in the DB
    """
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer
    lookup_field = None

    def get_queryset(self):
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender,
            size__in=preferences.size,
            age__in=convert_dog_age(preferences.age),
        )
        return dogs


#/api/dog/<pk>/undecided/
class RetrieveChangeStatus(RetrieveAPIView):
    """
    Create or retrieve UserDog instance, default status = undecided
    """
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer
    lookup_field = None

    def get_queryset(self):
        """ Retrieve all dogs based on chosen preferences """
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender,
            size__in=preferences.size,
            age__in=convert_dog_age(preferences.age),
        )
        return dogs

    def get_object(self):
        """ Get one dog to display and assign undefined status by default """
        user = self.request.user
        pk = self.kwargs.get('pk')
        dogs = self.get_queryset()
        dog = get_single_dog(dogs, pk)
        user_dog, created = models.UserDog.objects.get_or_create(
            user=user, dog=dog, status='u')
        return dog


def get_single_dog(dogs_query, pk):
    """ Look through the query of dogs """
    try:
        dog = dogs_query.filter(id=pk).get()
    except ObjectDoesNotExist:
        raise Http404
    return dog


def convert_dog_age(prefered_age):
    """
    Inspection of data range showed a dogs age between  2 and 96 months
    This function changes the selected preference into numerical ranges
    """
    prefered_age = prefered_age.split(",")
    dog_age = []
    for item in prefered_age:
        if item == "b":
            dog_age = [x for x in range(1,11)]
        elif item == "y":
            dog_age += [x for x in range(11,30)]
        elif item == "a":
            dog_age += [x for x in range(30,70)]
        elif item == "s":
            dog_age += [x for x in range(70,100)]
    return dog_age
