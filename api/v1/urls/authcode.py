from django.urls import path

from api.v1.views import (
    authcode as views_authcode
)

urlpatterns = [
    path('authcode/generate', views_authcode.AuthCodeGenerateView.as_view(), name='authcode-generate'),
    path('authcode/check', views_authcode.AuthCodeCheckView.as_view(), name='authcode-check'),
]
