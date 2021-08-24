from api.v1.views import (
    device as views_device,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import re_path

urlpatterns = [
    re_path(r'^device/(?P<device_uuid>[\w-]+)/detail/',
            views_device.DeviceDetailView.as_view(), name='device-detail'),
    re_path(r'^device_export/',
            views_device.DeviceExportView.as_view(), name='device-export'),
    re_path(r'^device/',
            views_device.DeviceListView.as_view(), name='device'),
]
