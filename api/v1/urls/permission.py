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
    # user
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_permission/(?P<user_uuid>[\w-]+)/create',
        views_permission.UserPermissionCreateView.as_view(),
        name='tenant-user-permission-create',
    ),
        re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_permission/(?P<user_uuid>[\w-]+)/delete/',
        views_permission.UserPermissionDeleteView.as_view(),
        name='tenant-user-permission-delete',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/user_permission/(?P<user_uuid>[\w-]+)/',
        views_permission.UserPermissionView.as_view(),
        name='tenant-user-permission',
    ),
    # group
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/group_permission/(?P<group_uuid>[\w-]+)/create',
        views_permission.GroupPermissionCreateView.as_view(),
        name='tenant-group-permission-create',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/group_permission/(?P<group_uuid>[\w-]+)/delete/',
        views_permission.GroupPermissionDeleteView.as_view(),
        name='tenant-group-permission-delete',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/group_permission/(?P<group_uuid>[\w-]+)/',
        views_permission.GroupPermissionView.as_view(),
        name='tenant-group-permission',
    ),
    # app
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app_permission/(?P<app_uuid>[\w-]+)/',
        views_permission.AppPermissionView.as_view(),
        name='tenant-app-permission',
    ),
]