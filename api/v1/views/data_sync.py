from .base import BaseViewSet
from api.v1.serializers.data_sync import DataSyncSerializer, DataSyncListSerializer
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from data_sync.models import DataSyncConfig
from rest_framework.decorators import action
from perm.custom_access import ApiAccessPermission
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code

DataSyncPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='DataSyncPolymorphicProxySerializer',
    serializers=get_app_runtime().data_sync_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='删除数据同步设置'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='批量更新数据同步设置'),
)
@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags=['data_sync'],
    parameters=[
        OpenApiParameter(
            name='sync_mode',
            type={'type': 'string'},
            enum=['server', 'client'],
            location=OpenApiParameter.QUERY,
            required=True,
        ),
    ]
)
class DataSyncViewSet(BaseViewSet):

    model = DataSyncConfig

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = DataSyncSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        sync_mode = self.request.query_params.get('sync_mode', None)
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
        }

        if sync_mode is not None:
            kwargs['sync_mode'] = sync_mode

        return DataSyncConfig.valid_objects.filter(**kwargs).order_by('id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = DataSyncConfig.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=DataSyncListSerializer,
        summary='数据更新列表',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=DataSyncPolymorphicProxySerializer,
        responses=DataSyncPolymorphicProxySerializer,
        summary='修改数据更新',
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=DataSyncPolymorphicProxySerializer,
        responses=DataSyncPolymorphicProxySerializer,
        summary='创建数据更新',
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        return super().create(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=DataSyncPolymorphicProxySerializer,
        summary='获取数据更新',
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
