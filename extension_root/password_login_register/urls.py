from django.urls import path
from . import views


urlpatterns = [
    path(
        "password_register",
        views.PasswordRegisterView.as_view(),
        name="password-register",
    ),
    path(
        "password_login",
        views.PasswordLoginView.as_view(),
        name="password-login",
    ),
]
