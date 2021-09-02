
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from auth_rules.views import TenantAuthRuleViewSet,AuthRuleAuthFactorChoicesListView,AuthRuleAppChoicesListView
from .tenant import tenant_router

router = DefaultRouter()

tenant_auth_rule_router = tenant_router.register(
    r'auth_rule',
    TenantAuthRuleViewSet,
    basename='tenant-auth-rule',
    parents_query_lookups=['tenant'],
)

urlpatterns = [
    re_path(
        r'^auth_rule/auth_factor_choices_list/$',
        AuthRuleAuthFactorChoicesListView.as_view(),
        name='auth-rule-auth-factor-choices-list',
    ),
    re_path(
        r'^auth_rule/app_choices_list/$',
        AuthRuleAppChoicesListView.as_view(),
        name='auth-rule-app-choices-list',
    ),
]