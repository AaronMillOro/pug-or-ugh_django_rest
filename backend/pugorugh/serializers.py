from django.contrib.auth import get_user_model

from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = get_user_model()


class DogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'image_filename', 'breed', 'age', 'gender', 'size')
        model = models.Dog


class UserDogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'dog', 'status')
        model = models.UserDog


class UserPrefSerializer(serializers.ModelSerializer):
    class Meta:
        extra_kwargs = {'user': {'write_only': True}}
        fields = ('age', 'gender', 'size')
        model = models.UserPref
