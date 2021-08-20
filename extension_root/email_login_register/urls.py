from django.urls import path
from . import views


urlpatterns = [
    path("email_register", views.EmailRegisterView.as_view(), name="email-register"),
    path(
        "email_reset_password",
        views.EmailResetPasswordView.as_view(),
        name="email-reset-password",
    ),
]
