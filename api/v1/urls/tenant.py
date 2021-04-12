from api.v1.views import (
    tenant as views_tenant,
)
from rest_framework_extensions.routers import ExtendedSimpleRouter
from django.urls import re_path


router = ExtendedSimpleRouter()
tenant_router = router.register(r'tenant', views_tenant.TenantViewSet, basename='tenant')

urlpatterns = [
    re_path(r'^tenant/(?P<slug>[\w-]+)/slug/$', views_tenant.TenantSlugView.as_view(), name='tenant-slug'),
]
