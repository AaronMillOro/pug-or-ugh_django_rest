from django.contrib.auth.models import User
from django.db import models


class Dog(models.Model):
    name = models.CharField(max_length=255, blank=True)
    image_filename = models.CharField(max_length=255)
    breed = models.CharField(max_length=255, blank=True)
    age = models.IntegerField()
    gender = models.CharField(
        max_length = 3,
        choices = [
            ('m', 'Male'),
            ('f', 'Female'),
            ('u', 'Unknown'),
        ],
        blank=True
    )
    size = models.CharField(
        max_length =5,
        choices = [
            ('s', 'Small'),
            ('m', 'Medium'),
            ('l', 'Large'),
            ('xl', 'Extra large'),
            ('u', 'Unknown'),
        ],
        blank=True
    )


class UserDog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status =models.CharField(
        max_length = 2,
        choices = [
            ('l', 'Liked'),
            ('d', 'Disliked'),
        ],
        blank=True
    )


class UserPref(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.CharField(
        max_length = 4,
        choices = [
            ('b', 'Baby'),
            ('y', 'Young'),
            ('a', 'Adult'),
            ('s', 'Senior'),
        ],
        blank=True
    )
    gender = models.CharField(
        max_length = 2,
        choices = [
            ('m', 'Male'),
            ('f', 'Female'),
        ],
        blank=True
    )
    size = models.CharField(
        max_length = 4,
        choices = [
            ('s', 'Small'),
            ('m', 'Medium'),
            ('l', 'Large'),
            ('xl', 'Extra large'),
        ],
        blank=True
    )
