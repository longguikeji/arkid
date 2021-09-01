#!/usr/bin/env python3


from django.urls import path

from api.v1.views import register

urlpatterns = [
    path('register/', register.RegisterView.as_view(), name='register'),
]
