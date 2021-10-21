from api.v1.views import (
    extension as views_extension
)

from .tenant import tenant_router


tenant_extension_router = tenant_router.register(r'extension', views_extension.ExtensionViewSet, basename='tenant-extension', parents_query_lookups=['tenant'])
