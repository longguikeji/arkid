from django.urls import path

from api.v1.views import (
    loginpage
)

urlpatterns = [
    path('loginpage/', loginpage.LoginPage.as_view(), name='loginpage'),
]