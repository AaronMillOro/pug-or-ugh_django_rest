# from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Dog(models.Model):
    name = models.CharField(max_length=255, blank=True)
    image_filename = models.CharField(max_length=255)
    breed = models.CharField(max_length=255, blank=True, default="")
    age = models.IntegerField()
    gender = models.CharField(
        max_length=1,
        choices=[('m', 'Male'), ('f', 'Female'), ('u', 'Unknown')]
    )
    size = models.CharField(
        max_length=1,
        choices=[('s', 'Small'), ('m', 'Medium'), ('l', 'Large'),
                 ('xl', 'Extra large'), ('u', 'Unknown')]
    )


class UserDog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2,
        choices=[('l', 'Liked'), ('d', 'Disliked')],
        blank=True
    )


class UserPref(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    age = models.CharField(
        max_length=4,
        choices=[('b', 'Baby'), ('y', 'Young'),
                 ('a', 'Adult'), ('s', 'Senior')],
        blank=True
    )
    gender = models.CharField(
        max_length=2,
        choices=[('m', 'Male'), ('f', 'Female')],
        blank=True
    )
    size = models.CharField(
        max_length=4,
        choices=[('s', 'Small'), ('m', 'Medium'),
                 ('l', 'Large'), ('xl', 'Extra large')],
        blank=True
    )
