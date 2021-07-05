from django.conf.urls import url
from django.urls import re_path
from django.urls import path
# dev
from .views.dev import IndexView


urlpatterns = [
    path('saml2sp/dev/index', IndexView.as_view(), name='index'),
]