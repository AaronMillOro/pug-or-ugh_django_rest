from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from pugorugh.views import UserRegisterView
from . import views

# API endpoints
urlpatterns = format_suffix_patterns([
    # favicon
    url(r'^favicon\.ico$', RedirectView.as_view(
        url='/static/icons/favicon.ico', permanent=True)),
    # index
    url(r'^$', TemplateView.as_view(template_name='index.html')),

    # User endpoints
    url(r'^api/user/login/$', obtain_auth_token,
        name='login-user'),
    url(r'^api/user/$', UserRegisterView.as_view(),
        name='register-user'),
    url(r'^api/user/preferences/$', views.UserPrefView.as_view(),
        name='user_prefer'),

    # Dogs endpoints
    url(r'^api/dogs/$', views.ListDogsView.as_view(), 
        name='list_dogs'),
    url(r'^api/dog/(?P<pk>\d+)/undecided/$',
        views.RetrieveChangeStatus.as_view(),
        name='retrive_undecided'),
])
