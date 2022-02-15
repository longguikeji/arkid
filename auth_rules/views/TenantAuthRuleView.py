from common.paginator import DefaultListPaginator
from api.v1.views.base import BaseViewSet
from runtime import get_app_runtime
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema_view
from openapi.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from auth_rules.models import TenantAuthRule
from auth_rules.serializers import BaseTenantAuthRuleSerializer, TenantAuthRuleListSerializer

TenantAuthRulePolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='TenantAuthRulePolymorphicProxySerializer',
    serializers=get_app_runtime().auth_rule_type_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags=['app'],
)
class TenantAuthRuleViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = BaseTenantAuthRuleSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return []
        qs = TenantAuthRule.active_objects.filter(tenant=tenant).order_by('id')
        return qs

    def get_object(self):
        uuid = self.kwargs['pk']
        context = self.get_serializer_context()
        tenant = context['tenant']

        return (
            TenantAuthRule.active_objects.filter(
                tenant=tenant,
                uuid=uuid,
            )
            .order_by('id')
            .first()
        )

    @extend_schema(roles=['tenant admin', 'global admin'], responses=TenantAuthRuleListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=TenantAuthRulePolymorphicProxySerializer,
        responses=TenantAuthRulePolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=TenantAuthRulePolymorphicProxySerializer,
        responses=TenantAuthRulePolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'], responses=TenantAuthRulePolymorphicProxySerializer
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)