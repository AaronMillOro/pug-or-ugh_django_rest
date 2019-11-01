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
    and dogs have 'undecided' status by default
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


#/api/dog/<pk>/<status>/next/
class RetrieveNextDog(RetrieveAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        """ Filterd dogs by User Preferences then by UserDog status """
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
        #print(list_ids)


#/api/dog/<pk>/<status>/
class RetrieveChangeStatus(UpdateAPIView):
    #permission_classes = (IsAuthenticated,)
    #authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    def get_queryset(self):
        """ Get dogs that match preferences"""
        user = self.request.user
        preferences = models.UserPref.objects.get(user=user.id)
        dogs = models.Dog.objects.filter(
            gender__in=preferences.gender.split(','),
            size__in=preferences.size.split(','),
            age__in=convert_dog_age(preferences.age),
        )
        return dogs

    def get_object(self):
        """ Get actual dog info """
        dog_id = self.kwargs.get('pk')
        dogs = self.get_queryset()
        # Check if queryset is empty
        if not dogs:
            raise Http404
        dog = self.get_queryset().filter(id__exact=dog_id)
        return dog

    def put(self, request, *args, **kwargs):
        """ Change status of selected dog """
        status = self.kwargs.get('status')
        dog = self.get_object()
        user = self.request.user

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
        return HttpResponse('')
"""
        def get(self):
            return next_dog
"""
