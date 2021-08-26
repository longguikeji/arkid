from api.v1.views import (
    authorization_agent as views_authorization_agent
)

from .tenant import tenant_router


tenant_authorization_agent_router = tenant_router.register(r'authorization_agent', views_authorization_agent.AuthorizationAgentViewSet, basename='tenant-authorization-agent', parents_query_lookups=['tenant'])
