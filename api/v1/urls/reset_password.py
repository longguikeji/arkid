#!/usr/bin/env python3


from django.urls import path

from api.v1.views import reset_password

urlpatterns = [
    path(
        'reset_password/', reset_password.ResetPWDView.as_view(), name='reset-password'
    ),
]
