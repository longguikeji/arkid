from extension_root.application_group.views import (
    ApplicationGroupViewSet as view_application_group,
)

from .tenant import tenant_router


tenant_application_group_router = tenant_router.register(
    r'application_group', view_application_group, basename='tenant-application_group', parents_query_lookups=['tenant'])
    

