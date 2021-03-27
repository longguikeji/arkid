from api.v1.views import (
    authorization_server as views_authorization_server
)

from .tenant import tenant_router


tenant_authorization_server_router = tenant_router.register(r'authorization_server', views_authorization_server.AuthorizationServerViewSet, basename='tenant-authorization-server', parents_query_lookups=['tenant'])
