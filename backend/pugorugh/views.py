from django.contrib.auth import get_user_model
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
            age__in=convert_dog_age(preferences.age),
            gender__in=preferences.gender,
            size__in=preferences.size,
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
        user = self.request.user
        preferences = models.UserPref.objects.get(user_id=user.id)
        dogs = models.Dog.objects.filter(
            age__in=convert_dog_age(preferences.age),
            gender__in=preferences.gender,
            size__in=preferences.size,
        )
        return dogs

    def get_object(self):
        pk = self.kwargs.get('pk')
        dogs = self.get_queryset()
        dog = get_single_dog(dogs, pk)
        return dog


def get_single_dog(dogs_query, pk):
    """ Loop through the query of dogs """
    try:
        dog = dogs_query.filter(id=pk).get()
    except DoesNotExist:
        dog = dogs.first()
    return dog


def convert_dog_age(prefered_age):
    """
    Inspection of data range showed a dogs age between  2 and 96 months
    This function changes the selected preference into numerical range
    """
    dog_age = []
    if "b" in prefered_age:
        dog_age = list(range(1,11))
    elif "y" in prefered_age:
        dog_age = list(range(11,30))
    elif "a" in prefered_age:
        dog_age = list(range(30,70))
    elif "s" in prefered_age:
        dog_age = list(range(70,100))
    else:
        print("Invalid code. Try again!")
        dog_age = list(range(1,11))
        # Default value (baby) is sent
    return dog_age

"""
class RetrieveDogView(generics.RetrieveAPIView):
    queryset = Dog.objects.all()
    serializer_class = DogSerializer

    def get_queryset(self):
        decision = self.kwargs.get('decision')

        preference = UserPref.objects.get(
            user=self.request.user)

        user_dog_queryset = UserDog.objects.filter(user=self.request.user)

        queryset = self.queryset.filter(
            age__in=preferred_dog_age(preference.age),
            gender__in=preference.gender,
            size__in=preference.size,
        )

        if decision == 'liked' or decision == 'disliked':
            dogs = queryset.filter(
                userdog__in=user_dog_queryset,
                userdog__status=decision[0]
            )
        else:
            dogs = queryset.filter(
                ~Q(userdog__in=user_dog_queryset) | Q(userdog__status='u')
            )

        return dogs

    def get_object(self):
        pk = self.kwargs.get('pk')
        queryset = self.get_queryset()
        dog = retrieve_single_dog(queryset, pk)

        if not dog:
            raise Http404

        return dog


def retrieve_single_dog(dogs, pk):
    Retrieve single dog and loop back when user went through all dogs.
    try:
        dog = dogs.filter(id__gt=pk)[:1].get()
    except ObjectDoesNotExist:
        dog = dogs.first()
    return dog
"""
