from api.v1.views import (
    permission as views_permission,
)

from .tenant import tenant_router
from django.urls import re_path

tenant_router.register(r'permission',
        views_permission.PermissionViewSet,
        basename='tenant-permission',
        parents_query_lookups=['tenant',])

urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/permission/create',
        views_permission.PermissionCreateView.as_view(),
        name='tenant-permission-create',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/permission/(?P<permission_uuid>[\w-]+)/detail',
        views_permission.PermissionView.as_view(),
        name='tenant-permission-detail',
    ),
]