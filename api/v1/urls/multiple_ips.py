from extension_root.application_multiple_ip.views import (
    ApplicationMultipleIpViewSet as view_multiple_ips
)

from .tenant import tenant_router


tenant_multiple_ips_router = tenant_router.register(
    r'multiple_ips', view_multiple_ips, basename='tenant-multiple_ips', parents_query_lookups=['tenant'])
