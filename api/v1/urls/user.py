from api.v1.views import (
    user as views_user,
    permission as views_permission,
)

from .tenant import tenant_router

tenant_user_router = tenant_router.register(r'user', views_user.UserViewSet, basename='tenant-user', parents_query_lookups=['tenant'])

tenant_user_router.register(r'app',
    views_user.UserAppViewSet,
    basename='tenant-user-app',
    parents_query_lookups=['tenant', 'user'])