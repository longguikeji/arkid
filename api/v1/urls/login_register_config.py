from api.v1.views import (
    login_register_config as views_config,
)

from .tenant import tenant_router


tenant_external_idp_router = tenant_router.register(
    r'login_register_config',
    views_config.LoginRegisterConfigViewSet,
    basename='tenant-login-register-config',
    parents_query_lookups=['tenant'],
)
