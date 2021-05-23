from api.v1.views import app as views_app

from .tenant import tenant_router

tenant_app_router = tenant_router.register(
    r'app',
    views_app.AppViewSet,
    basename='tenant-app',
    parents_query_lookups=['tenant'],
)

tenant_app_router.register(
    r'provisioning',
    views_app.AppProvisioningViewSet,
    basename='tenant-app-provisioning',
    parents_query_lookups=['tenant', 'app'],
)
