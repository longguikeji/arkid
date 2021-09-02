
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from auth_rules.views import TenantAuthRuleViewSet
from .tenant import tenant_router

router = DefaultRouter()

tenant_auth_rule_router = tenant_router.register(
    r'auth_rule',
    TenantAuthRuleViewSet,
    basename='tenant-auth-rule',
    parents_query_lookups=['tenant'],
)

urlpatterns = []