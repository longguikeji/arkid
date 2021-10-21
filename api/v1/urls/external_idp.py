from api.v1.views import (
    external_idp as views_external_idp
)

from .tenant import tenant_router


tenant_external_idp_router = tenant_router.register(r'external_idp', views_external_idp.ExternalIdpViewSet, basename='tenant-external-idp', parents_query_lookups=['tenant'])
