from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    path(
        "email_reset_password",
        views.EmailResetPasswordView.as_view(),
        name="email-reset-password",
    ),
]
