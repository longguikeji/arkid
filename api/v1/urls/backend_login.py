#!/usr/bin/env python3
from django.urls import path

from api.v1.views import backend_login

urlpatterns = [
    path(
        'backend_login/', backend_login.BackendLoginView.as_view(), name='backend-login'
    ),
]
