from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateAPIView, RetrieveAPIView,
                                     UpdateAPIView)
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
    Get and update User preferences
    Each time preferences are set UserDog instances are reseted
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

    def get_queryset(self):
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
            age__in=convert_dog_age(preferences.age),
        )
        return dogs


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


def get_single_dog(dogs_query, dog_id):
    """ Function to view through dogs query and get ONE dog """
    dog = dogs_query.filter(id__gt=dog_id).first()
    if dog is not None:
        return dogs_query.first()
    else:
        return dog


#/api/dog/<pk>/<status>/next/
class RetrieveNextDog(RetrieveAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        """ Filterd dogs by User Preferences the by UserDog status """
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
            age__in=convert_dog_age(preferences.age))
        status = self.kwargs.get('status')
        if status == 'undecided':
            dogs = dogs.filter(userdog__status__exact='u').order_by('pk')
        elif status == 'liked':
            dogs = dogs.filter(userdog__status__exact='l').order_by('pk')
        else:
            dogs = dogs.filter(userdog__status__exact='d').order_by('pk')
        return dogs

    def get_object(self):
        dog_id = self.kwargs.get('pk')
        dogs = self.get_queryset()
        # Check if queryset is empty
        if not dogs:
            raise Http404
        dog = self.get_queryset().filter(id__gt=dog_id).first()
        if dog is not None:
            return dog
        else:
            dog = self.get_queryset().first()
            return dog

        #list_ids = [item.pk for item in dogs] # generate list of ids
        #next_dog = dogs.only('pk').order_by('?').first()
        #print(list_ids)


#/api/dog/<pk>/<status>/
class RetrieveChangeStatus(RetrieveUpdateAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
            age__in=convert_dog_age(preferences.age),
        )
        return dogs

    def get_object(self):
        user = self.request.user
        dog_id = self.kwargs.get('pk')
        dogs = self.get_queryset()
        # Check if queryset is empty
        if not dogs:
            raise Http404
        dog = self.get_queryset().filter(id__gt=dog_id).first()
        if dog is not None:
            return dog
        else:
            dog = self.get_queryset().first()
            return dog

        status = self.kwargs.get('status')

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

"""

#/api/dog/<pk>/<status>/next/
class RetrieveStatus(RetrieveAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer
    lookup_field = None

    def get_queryset(self):
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
        dogs = models.Dog.objects.filter(id__in=list_dogs,).order_by('id')
        return dogs

    def get_object(self):
        user = self.request.user
        pk = int(self.kwargs.get('pk'))
        dogs = self.get_queryset()
        dog = get_single_dog2(dogs, pk)
        print(pk, dog.id, dogs, dog)
        return dog


def get_single_dog2(dogs_query, pk):
    if len(dogs_query) > 1:
        try:
            dog = dogs_query.filter(id__gt=pk).first()
        except ObjectDoesNotExist:
            dog = dogs_query.first()
    else:
        dog = dogs_query.first()
    return dog
"""
