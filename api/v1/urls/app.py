from api.v1.views import app as views_app
from django.urls import re_path
from .tenant import tenant_router
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

tenant_app_router = tenant_router.register(
    r'app',
    views_app.AppViewSet,
    basename='tenant-app',
    parents_query_lookups=['tenant'],
)

urlpatterns = [
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app/(?P<app_uuid>[\w-]+)/provisioning/$',
        views_app.AppProvisioningView.as_view(),
        name='app-provisioning-config',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app/(?P<app_uuid>[\w-]+)/provisioning/mapping/$',
        views_app.AppProvisioningMappingView.as_view(),
        name='app-provisioning-config-mapping',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app/(?P<app_uuid>[\w-]+)/provisioning/mapping/(?P<map_uuid>[\w-]+)/$',
        views_app.AppProvisioningMappingDetailView.as_view(),
        name='app-provisioning-config-mapping-detail',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app/(?P<app_uuid>[\w-]+)/provisioning/profile/$',
        views_app.AppProvisioningProfileView.as_view(),
        name='app-provisioning-config-profile',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app/(?P<app_uuid>[\w-]+)/provisioning/profile/(?P<profile_uuid>[\w-]+)/$',
        views_app.AppProvisioningProfileDetailView.as_view(),
        name='app-provisioning-config-profile-detail',
    ),
    re_path(
        r'^tenant/(?P<tenant_uuid>[\w-]+)/app_list/',
        views_app.AppListAPIView.as_view(),
        name='tenant-app-list',
    ),
    re_path(
        r'^app/app_permission_check/',
        views_app.AppPermissionCheckView.as_view(),
        name='app-permission-check',
    ),
]
