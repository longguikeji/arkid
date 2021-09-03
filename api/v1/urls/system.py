from django.urls import path, re_path

from api.v1.views import system as views_system

urlpatterns = [
    path(
        'system/config', views_system.SystemConfigView.as_view(), name='system-config'
    ),
    # re_path(
    #     r'^system/config/privacy_notice/$',
    #     views_system.SystemPrivacyNoticeView.as_view(),
    #     name='system-privacy_notice',
    # ),
]
