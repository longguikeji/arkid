from api.v1.views import (
    tenant as views_tenant,
)

from rest_framework_extensions.routers import ExtendedSimpleRouter


router = ExtendedSimpleRouter()


tenant_router = router.register(r'tenant', views_tenant.TenantViewSet, basename='tenant')

urlpatterns = router.urls