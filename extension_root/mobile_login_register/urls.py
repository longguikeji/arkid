from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    path(
        "mobile_reset_password",
        views.MobileResetPasswordView.as_view(),
        name="mobile-reset-password",
    ),
]
