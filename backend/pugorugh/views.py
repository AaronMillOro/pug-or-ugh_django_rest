from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                    RetrieveAPIView, RetrieveUpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    Choose at least one of each category.
    age : Baby(b), Young(y), Adult(a) and Senior(s)
    gender : Male(m) and Female(f)
    size : Small(s), Medium(m), Large(l) and Extra large(xl)
    Each time preferences are set the UserDog instances are reseted
    for the current user
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
        finally:
            dogs = models.Dog.objects.filter(
                gender__in=user_pref.gender.split(','),
                size__in=user_pref.size.split(','),
                age__in=convert_dog_age(user_pref.age),
            )
            models.UserDog.objects.filter(user=user).delete()
            for dog in dogs:
                user_dog = models.UserDog.objects.create(user=user, dog=dog)
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
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
            age__in=convert_dog_age(preferences.age),
        )
        return dogs


#/api/dog/<pk>/<status>/
class RetrieveChangeStatus(RetrieveUpdateAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer
    lookup_field = None

    def get_queryset(self):
        """
        Retrieve dogs based on chosen preferences
        """
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
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

        #/api/dog/<pk>/undecided/
        if status == 'undecided':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'u'
                user_dog.save()
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(user=user, dog=dog)

        #/api/dog/<pk>/liked/
        elif status == 'liked':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'l'
                user_dog.save()
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(
                    user=user, dog=dog, status='l')

        #/api/dog/<pk>/disliked/
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
    """
    Look through the query of dogs and return ONE dog
    Unless the dog is not present in the queryset
    """
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
    prefered_age = prefered_age.split(',')
    dog_age = []
    for item in prefered_age:
        if item == 'b':
            dog_age = [x for x in range(1,11)]
        elif item == 'y':
            dog_age += [x for x in range(11,30)]
        elif item == 'a':
            dog_age += [x for x in range(30,70)]
        elif item == 's':
            dog_age += [x for x in range(70,100)]
    return dog_age


#/api/dog/<pk>/<status>/next/
class RetrieveStatus(RetrieveAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer
    lookup_field = None

    def get_queryset(self):
        """ Retrieve undecided dogs """
        user = self.request.user
        status = self.kwargs.get('status')
        if status == 'undecided':
            user_dog = models.UserDog.objects.filter(user=user.id, status='u')
        elif status == 'liked':
            user_dog = models.UserDog.objects.filter(user=user.id, status='l')
        elif status == 'disliked':
            user_dog = models.UserDog.objects.filter(user=user.id, status='d')
        else:
            raise Http404
        list_dogs = [dog.dog_id for dog in user_dog]
        dogs = models.Dog.objects.filter(id__in=list_dogs,)
        return dogs

    def get_object(self):
        user = self.request.user
        pk = self.kwargs.get('pk')
        dogs = self.get_queryset()
        dog = get_single_dog(dogs, pk)
        return dog
