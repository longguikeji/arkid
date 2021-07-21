from django.urls import path, re_path

from api.v1.views import system as views_system

urlpatterns = [
    re_path(
        r'^system/config/(?P<subject>[\w-]+)/$',
        views_system.SystemConfigView.as_view(),
        name='system-config-subject',
    ),
]
