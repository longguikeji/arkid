from django.urls import path

from api.v1.views import (
    login as views_login,    
    loginpage
)

urlpatterns = [
    path('login/', views_login.LoginView.as_view(), name='login'),
    path('mobile_login/', views_login.MobileLoginView.as_view(), name='mobile-login'),
    path('username_register/', views_login.UserNameRegisterView.as_view(), name='username-register'),
    path('mobile_register/', views_login.MobileRegisterView.as_view(), name='mobile-register'),
    path('loginpage/', loginpage.LoginPage.as_view(), name='loginpage'),
]