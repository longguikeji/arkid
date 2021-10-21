from api.v1.views import (
    group as views_group
)

from .tenant import tenant_router

tenant_group_router = tenant_router.register(r'group', views_group.GroupViewSet, basename='tenant-group', parents_query_lookups=['tenant'])