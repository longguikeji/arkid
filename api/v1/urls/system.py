from django.urls import path

from api.v1.views import (
    system as views_system
)

urlpatterns = [
    path('system/config', views_system.SystemConfigView.as_view(), name='system-config'),
]
