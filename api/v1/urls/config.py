#!/usr/bin/env python3


from api.v1.views import (
    config as views_config,
)
from django.urls import path, re_path
from .tenant import tenant_router

tenant_router.register(
    r'config/custom_field',
    views_config.CustomFieldViewSet,
    basename='tenant-custom-field',
    parents_query_lookups=['tenant'],
)

urlpatterns = [
    re_path(
        r'^config/native_field/$',
        views_config.NativeFieldListAPIView.as_view(),
        name='native_field_list',
    ),
    re_path(
        r'^config/native_field/(?P<uuid>[\w]+)/$',
        views_config.NativeFieldDetailAPIView.as_view(),
        name='native_field_detail',
    ),
    re_path(
        r'^config/privacy_notice/$',
        views_config.PrivacyNoticeView.as_view(),
        name='privacy_notice',
    ),
    # re_path(
    #     r'^config/password_complexity/(?P<complexity_uuid>[\w-]+)/',
    #     views_config.PasswordComplexityDetailView.as_view(),
    #     name='password-complexity-detail',
    # ),
    # re_path(
    #     r'^config/password_complexity/',
    #     views_config.PasswordComplexityView.as_view(),
    #     name='password-complexity',
    # ),
    re_path(
        r'^config/current_password_complexity/',
        views_config.CurrentPasswordComplexityView.as_view(),
        name='current-password-complexity',
    ),
]
