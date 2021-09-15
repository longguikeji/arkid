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
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/permission_group/create',
        views_permission.PermissionGroupCreateView.as_view(),
        name='tenant-permission-group-create',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/permission_group/(?P<permission_group_uuid>[\w-]+)/detail',
        views_permission.PermissionGroupDetailView.as_view(),
        name='tenant-permission-group-detail',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/permission_group/',
        views_permission.PermissionGroupView.as_view(),
        name='tenant-permission-group',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_permission/(?P<user_uuid>[\w-]+)/',
        views_permission.UserPermissionView.as_view(),
        name='tenant-user-permission',
    ),
]