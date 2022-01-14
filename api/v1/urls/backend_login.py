#!/usr/bin/env python3
from api.v1.views import (
    backend_login as views_backend_login
)

from .tenant import tenant_router


tenant_backend_login_router = tenant_router.register(
    r'backend_login', views_backend_login.BackendLoginViewSet, basename='tenant-backend-login', parents_query_lookups=['tenant'])
