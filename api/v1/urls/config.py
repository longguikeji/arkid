#!/usr/bin/env python3


from api.v1.views import (
    config as views_config,
)
from django.urls import path
from django.conf.urls import url

from .tenant import tenant_router

tenant_router.register(r'config/custom_field', views_config.CustomFieldViewSet, basename='tenant-custom-field', parents_query_lookups=['tenant'])

urlpatterns = [
    url(r'^config/native_field/$', views_config.NativeFieldListAPIView.as_view(), name='native_field_list'),
    url(r'^config/native_field/(?P<uuid>[\w]+)/$', views_config.NativeFieldDetailAPIView.as_view(), name='native_field_detail'),
]
