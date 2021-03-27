from api.v1.views import (
    permission as views_permission,
)

from .tenant import tenant_router

tenant_router.register(r'permission',
        views_permission.PermissionViewSet,
        basename='tenant-permission',
        parents_query_lookups=['tenant',])
