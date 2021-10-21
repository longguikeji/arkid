
from django.urls import path
from . import views


urlpatterns = [
    path('miniprogram/login', views.MiniProgramLoginView.as_view(), name='login'),
    path('miniprogram/bind', views.MiniProgramBindAPIView.as_view(), name='bind'),
    path('miniprogram/unbind', views.MiniProgramUnBindAPIView.as_view(), name='unbind'),
]
