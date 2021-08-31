#!/usr/bin/env python3


from django.urls import path

from api.v1.views import login

urlpatterns = [
    path('login/', login.LoginView.as_view(), name='login'),
]
