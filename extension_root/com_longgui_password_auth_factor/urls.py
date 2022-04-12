from django.urls import path
from . import views


urlpatterns = [
    # path(
    #     "password_register",
    #     views.PasswordRegisterView.as_view(),
    #     name="password-register",
    # ),
    # path(
    #     "password_login",
    #     views.PasswordLoginView.as_view(),
    #     name="password-login",
    # ),
    path(
        "login_fields",
        views.LoginFieldsView.as_view(),
        name="login-fields",
    ),
    path(
        "register_fields",
        views.RegisterFieldsView.as_view(),
        name="register-fields",
    ),
]
