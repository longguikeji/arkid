from api.v1.views import (
    tenant as views_tenant,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import re_path


router = ExtendedSimpleRouter()
tenant_router = router.register(r'tenant', views_tenant.TenantViewSet, basename='tenant')

urlpatterns = [
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/config/', views_tenant.TenantConfigView.as_view(), name='tenant-config'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/password_complexity/(?P<complexity_uuid>[\w-]+)/detail/', views_tenant.TenantPasswordComplexityDetailView.as_view(), name='tenant-password-complexity-detail'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/password_complexity/', views_tenant.TenantPasswordComplexityView.as_view(), name='tenant-password-complexity'),
    re_path(r'^tenant/(?P<tenant_uuid>[\w-]+)/current_password_complexity/', views_tenant.TenantCurrentPasswordComplexityView.as_view(), name='tenant-current-password-complexity'),
    re_path(r'^tenant/(?P<slug>[\w-]+)/slug/$', views_tenant.TenantSlugView.as_view(), name='tenant-slug'),
]
