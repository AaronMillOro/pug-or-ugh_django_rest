from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.test import (APIClient, APIRequestFactory, APITestCase,
                                 force_authenticate)
from . import models
from . import views


class UnitModelsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='jonny', password='1234F!#$k')

    def test_user_created(self):
        user2 = User.objects.create(
            username='jean', password='qwertyui12345'
        )
        users = len(User.objects.all())
        self.assertEqual(users, 2)

    def test_user_preferences(self):
        user = models.User.objects.get(username='jonny')
        user_pref = models.UserPref.objects.create(
            age='b,y,a,s',
            gender='m,f',
            size='s,m',
            user_id=user.id
        )
        self.assertEqual(user_pref.age, 'b,y,a,s')
        self.assertNotEqual(user_pref.gender, 'f')

    def test_dog(self):
        dog = models.Dog.objects.create(
            name='Muffin', image_filename='3.jpg', breed='Boxer',
            age=24, gender='f', size='xl'
        )
        dog_test = models.Dog.objects.get(name='Muffin')
        self.assertEqual(dog_test.size, 'xl')
        self.assertNotEqual(dog_test.gender, 'm')

    def test_user_dog(self):
        user = models.User.objects.get(username='jonny')
        dog = models.Dog.objects.create(
            name='Muffin', image_filename='3.jpg', breed='Boxer',
            age=24, gender='f', size='xl'
        )
        userdog = models.UserDog.objects.create(user=user, dog=dog)
        self.assertEqual(userdog.status, 'u')


class UnitTestViews(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='jonny', password='12#$k')
        self.dog1 = models.Dog.objects.create(
            name='Francesca', image_filename='1.jpg', breed='Labrador',
            age=72, gender='f', size='l'
        )
        self.dog2 = models.Dog.objects.create(
            name='Muffin', image_filename='3.jpg', breed='Boxer',
            age=24, gender='f', size='xl'
        )
        self.user_pref = models.UserPref.objects.create(
            age='b,y,a,s', gender='m,f', size='s,m',
            user_id=self.user.id
        )
        self.user_dog = models.UserDog.objects.create(
            user=self.user,
            dog=self.dog1,
            status='u'
        )

    def test_user_register_view(self):
        view = views.UserRegisterView.as_view()
        request = self.factory.post(
            'register-user', {'username': 'User2', 'password': 'pass123'})
        user3 = User.objects.create(username='ruma', password='12$k')
        user = User.objects.all().first()
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.User.objects.count(), 3)

    def test_user_preferences_view(self):
        view = views.UserPrefView.as_view()
        user = self.user
        user_pref = {'age': 'b,y,a,s', 'gender': 'm,f',
                     'size': 's,m', 'id': user.id}
        request = self.factory.put('user_prefer', kwargs=user_pref)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'age': 'b,y,a,s', 'gender': 'm,f',
                                         'size': 's,m'})

    def test_next_dog_view(self):
        view = views.RetrieveNextDog.as_view()
        user = self.user
        dog = self.dog1
        kwargs = {'pk': dog.id, 'status': 'undecided'}
        request = self.factory.get(reverse('next_dog', kwargs=kwargs))
        force_authenticate(request, user=user)
        response = view(request, pk='1', decision='undecided')
        self.assertTrue(response.status_code)

    def test_change_dog_status_view(self):
        self.client = APIClient()
        view = views.RetrieveChangeStatus.as_view()
        request = self.factory.put(reverse(
            'change_status', kwargs={'pk': 1, 'status': 'liked'}))
        force_authenticate(request, user=self.user)
        response = view(request, pk='1', decision='liked')
        self.assertTrue(response.status_code)
