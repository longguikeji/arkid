
from django.urls import re_path
from django.urls import path
from . import views


urlpatterns = [
    path("userconfig", views.TenantUserConfigView.as_view(), name='tenant-userconfig'),
    path("userfields", views.TenantUserConfigFieldView.as_view(), name='tenant-userfields'),
]
