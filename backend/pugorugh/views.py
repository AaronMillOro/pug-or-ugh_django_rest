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
    View to inspect all the dogs present in queryset
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


#/api/dog/<pk>/<status>/next
class RetrieveChangeStatus(RetrieveUpdateAPIView):
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
        """
        Get one dog to display and assign one of the diffent status:
        undecided, liked or disliked
        The queryset will be obtained in function of the User preferences
        No dog can be repeated in the UserDog model
        """
        user = self.request.user
        pk = self.kwargs.get('pk')
        status = self.kwargs.get('status')
        dogs = self.get_queryset()
        dog = get_single_dog(dogs, pk)

        #/api/dog/<pk>/undecided/next
        if status == 'undecided':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'u'
                user_dog.save()
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(user=user, dog=dog)

        #/api/dog/<pk>/liked/next
        elif status == 'liked':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'l'
                user_dog.save()
            except ObjectDoesNotExist:
                    user_dog = models.UserDog.objects.create(
                        user=user, dog=dog, status='l')

        #/api/dog/<pk>/disliked/next
        elif status == 'disliked':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'd'
                user_dog.save()
            except ObjectDoesNotExist:
                    user_dog = models.UserDog.objects.create(
                        user=user, dog=dog, status='d')
        return dog


def get_single_dog(dogs_query, pk):
    """ Look through the query of dogs and return ONE dog"""
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
