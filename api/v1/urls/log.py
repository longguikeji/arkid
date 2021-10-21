from api.v1.views import (
    log as views_log,
)

from .tenant import tenant_router


tenant_router.register(r'user_log',
        views_log.UserLogViewSet,
        basename='tenant-user-log',
        parents_query_lookups=['tenant',])

tenant_router.register(r'admin_log',
        views_log.AdminLogViewSet,
        basename='tenant-admin-log',
        parents_query_lookups=['tenant',])

tenant_router.register(r'log',
        views_log.LogViewSet,
        basename='tenant-log',
        parents_query_lookups=['tenant',])
