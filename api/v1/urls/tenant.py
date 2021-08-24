from api.v1.views import (
    tenant as views_tenant,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import re_path


router = ExtendedSimpleRouter()
tenant_router = router.register(
    r'tenant', views_tenant.TenantViewSet, basename='tenant'
)

urlpatterns = [
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/config/',
            views_tenant.TenantConfigView.as_view(), name='tenant-config'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/password_complexity/(?P<complexity_uuid>[\w-]+)/detail/',
            views_tenant.TenantPasswordComplexityDetailView.as_view(), name='tenant-password-complexity-detail'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/password_complexity/',
            views_tenant.TenantPasswordComplexityView.as_view(), name='tenant-password-complexity'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/current_password_complexity/',
            views_tenant.TenantCurrentPasswordComplexityView.as_view(), name='tenant-current-password-complexity'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contactsconfig/function_switch/',
            views_tenant.TenantContactsConfigFunctionSwitchView.as_view(), name='tenant-contactsconfig-function-switch'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contactsconfig/info_visibility/(?P<info_uuid>[\w-]+)/detail/',
            views_tenant.TenantContactsConfigInfoVisibilityDetailView.as_view(), name='tenant-contactsconfig-info-visibility-detail'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contactsconfig/info_visibility/',
            views_tenant.TenantContactsConfigInfoVisibilityView.as_view(), name='tenant-contactsconfig-info-visibility'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contactsconfig/(?P<group_uuid>[\w-]+)/group_visibility/',
            views_tenant.TenantContactsConfigGroupVisibilityView.as_view(), name='tenant-contactsconfig-group-visibility'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contacts/group/',
            views_tenant.TenantContactsGroupView.as_view(), name='tenant-contacts-group'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contacts/user/',
            views_tenant.TenantContactsUserView.as_view(), name='tenant-contacts-user'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/contacts/user_tags/',
            views_tenant.TenantContactsUserTagsView.as_view(), name='tenant-contacts-user-tags'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/privacy_notice/',
            views_tenant.TenantPrivacyNoticeView.as_view(), name='tenant-privacy_notice'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/desktopconfig/',
            views_tenant.TenantDesktopConfigView.as_view(), name='tenant-desktop-config'),
    re_path(r'^tenant/(?P<slug>[\w-]+)/slug/$',
        views_tenant.TenantSlugView.as_view(), name='tenant-slug'),
]
