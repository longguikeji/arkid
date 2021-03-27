from django.urls import path

from api.v1.views import (
    login as views_login,    
)

urlpatterns = [
    path('login/', views_login.LoginView.as_view()),
    path('mobile_login/', views_login.MobileLoginView.as_view()),
]