from api.v1.views import (
    extension as views_extension
)

from .tenant import tenant_router

tenant_marketplace_router = tenant_router.register(r'marketplace', views_extension.ExtensionViewSet, basename='tenant-marketplace', parents_query_lookups=['tenant'])
