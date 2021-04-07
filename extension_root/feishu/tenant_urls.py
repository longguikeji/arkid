
from django.urls import path
from . import views


urlpatterns = [
    path('feishu/login', views.FeishuLoginView.as_view(), name='login'),
    path('feishu/callback', views.FeishuCallbackView.as_view(), name='callback'),
]
