from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import (CreateAPIView, RetrieveUpdateAPIView,
                                     RetrieveAPIView, UpdateAPIView)
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
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
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


def convert_dog_age(prefered_age):
    """
    Inspection of data range showed a dogs age between  2 and 96 months
    This function changes the selected preference into numerical ranges
    """
    prefered_age = prefered_age.split(',')
    dog_age = []
    for item in prefered_age:
        if item == 'b':
            dog_age = [x for x in range(1, 11)]
        elif item == 'y':
            dog_age += [x for x in range(11, 30)]
        elif item == 'a':
            dog_age += [x for x in range(30, 70)]
        elif item == 's':
            dog_age += [x for x in range(70, 100)]
    return dog_age


def get_single_dog(dogs_query, pk):
    """ Function to retrieve a single dog from a query """
    dog = dogs_query.filter(id__gt=pk).first()
    if dog is not None:
        return dog
    else:
        return dogs_query.first()


# /api/dog/<pk>/<status>/next/
class RetrieveNextDog(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
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
        dog = get_single_dog(dogs, dog_id)
        return dog


# /api/dog/<pk>/<status>/
class RetrieveChangeStatus(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
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
        if not dogs:
            raise Http404
        dog = self.get_queryset().filter(id__exact=dog_id)
        return dog

    def put(self, request, *args, **kwargs):
        """ Change status of selected dog """
        # These variables are useful for the change of status
        status = self.kwargs.get('status')
        dog = self.get_object()
        user = self.request.user
        # These are useful for the post PUT event
        dogs = self.get_queryset()
        dog_id = self.kwargs.get('pk')

        # /api/dog/<pk>/undecided/
        if status == 'undecided':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'u'
                user_dog.save()
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(user=user, dog=dog)
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)

        # /api/dog/<pk>/liked/
        elif status == 'liked':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'l'
                user_dog.save()
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(
                    user=user, dog=dog, status='l')
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)

        # /api/dog/<pk>/disliked/
        elif status == 'disliked':
            try:
                user_dog = models.UserDog.objects.get(user=user, dog=dog)
                user_dog.status = 'd'
                user_dog.save()
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)
            except ObjectDoesNotExist:
                user_dog = models.UserDog.objects.create(
                    user=user, dog=dog, status='d')
                next_dog = get_single_dog(dogs, dog_id)
                serializer = serializers.DogSerializer(next_dog)
                return Response(serializer.data)

        return HttpResponse('')
