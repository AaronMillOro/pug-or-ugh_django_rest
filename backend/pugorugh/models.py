from django.contrib.auth.models import User
from django.db import models


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
        max_length=2,
        choices=[('s', 'Small'), ('m', 'Medium'), ('l', 'Large'),
                 ('xl', 'Extra large'), ('u', 'Unknown')]
    )

    def __str__(self):
        return self.name


class UserDog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=[('l', 'Liked'), ('d', 'Disliked')],
        default='u',
    )


class UserPref(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.CharField(max_length=8, default='b,y,a,s')
    gender = models.CharField(max_length=4, default='m,f')
    size = models.CharField(max_length=9, default='s,m,l,xl')
