from django.urls import path

from api.v1.views import (
    login as views_login,    
    loginpage
)

urlpatterns = [
    path('login/', views_login.LoginView.as_view()),
    path('mobile_login/', views_login.MobileLoginView.as_view()),
    path('loginpage/', loginpage.LoginPage.as_view()),
]