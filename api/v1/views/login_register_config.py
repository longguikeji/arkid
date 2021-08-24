from .base import BaseViewSet
from api.v1.serializers.login_register_config import (
    LoginRegisterConfigSerializer,
    LoginRegisterConfigListSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from login_register_config.models import LoginRegisterConfig
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code
from drf_spectacular.utils import extend_schema_view, OpenApiParameter
from tenant.models import Tenant

LoginRegisterConfigPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='LoginRegisterConfigPolymorphicProxySerializer',
    serializers=get_app_runtime().login_register_config_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags=['login_register_config'],
    roles=['tenant admin', 'global admin'],
    parameters=[
        OpenApiParameter(
            name='tenant',
            type={'type': 'string'},
            location=OpenApiParameter.QUERY,
            required=True,
        )
    ],
)
class LoginRegisterConfigViewSet(BaseViewSet):

    model = LoginRegisterConfig

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = LoginRegisterConfigSerializer

    def get_queryset(self):

        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()
        kwargs = {
            'tenant': tenant,
        }

        return LoginRegisterConfig.valid_objects.filter(**kwargs)

    def get_object(self):
        tenant_uuid = self.request.query_params.get('tenant')
        if not tenant_uuid:
            tenant_uuid = None
        else:
            tenant = Tenant.valid_objects.filter(uuid=tenant_uuid).first()

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = LoginRegisterConfig.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=LoginRegisterConfigListSerializer,
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=LoginRegisterConfigPolymorphicProxySerializer,
        responses=LoginRegisterConfigPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        request=LoginRegisterConfigPolymorphicProxySerializer,
        responses=LoginRegisterConfigPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenant admin', 'global admin'],
        responses=LoginRegisterConfigPolymorphicProxySerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
