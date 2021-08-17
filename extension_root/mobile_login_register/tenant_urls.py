from django.urls import path
from . import views


urlpatterns = [
    path("mobile_login", views.MobileLoginView.as_view(), name="mobile-login"),
    path("mobile_register", views.MobileRegisterView.as_view(), name="mobile-register"),
    # path(
    #     "mobile_reset_password",
    #     views.MobileResetPasswordView.as_view(),
    #     name="mobile-reset-password",
    # ),
]
