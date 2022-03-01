from .base import BaseViewSet
from api.v1.serializers.external_idp import (
    ExternalIdpSerializer,
    ExternalIdpListSerializer,
    ExternalIdpReorderSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from perm.custom_access import ApiAccessPermission
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from external_idp.models import ExternalIdp
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code

ExternalIdpPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExternalIdpPolymorphicProxySerializer',
    serializers=get_app_runtime().external_idp_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'], summary='删除外部插件'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin']),
)
@extend_schema(tags=['external_idp'])
class ExternalIdpViewSet(BaseViewSet):

    model = ExternalIdp

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = ExternalIdpSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
        }

        return ExternalIdp.valid_objects.filter(**kwargs).order_by('order_no', 'id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = ExternalIdp.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'], responses=ExternalIdpListSerializer, summary='外部插件列表')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        request=ExternalIdpPolymorphicProxySerializer,
        responses=ExternalIdpPolymorphicProxySerializer,
        summary='修改外部插件',
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        request=ExternalIdpPolymorphicProxySerializer,
        responses=ExternalIdpPolymorphicProxySerializer,
        summary='创建外部插件',
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()

        return super().create(request, *args, **kwargs)

    @extend_schema(roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'], responses=ExternalIdpPolymorphicProxySerializer, summary='获得外部插件')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        request=ExternalIdpReorderSerializer,
        responses=ExternalIdpReorderSerializer,
        summary='修改外部插件'
    )
    @action(detail=False, methods=['post'])
    def batch_update(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        idp_uuid_list = request.data.get('idps')
        idps = ExternalIdp.valid_objects.filter(
            uuid__in=idp_uuid_list, tenant=tenant
        ).order_by('order_no')
        original_order_no = [idp.order_no for idp in idps]
        index = 0
        for uuid in idp_uuid_list:
            idp = idps.filter(uuid=uuid).first()
            if not idp:
                continue
            idp.order_no = original_order_no[index]
            idp.save()
            index += 1
        return JsonResponse(
            data={
                'error': Code.OK.value,
            }
        )

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        responses=ExternalIdpReorderSerializer,
        summary='外部插件上移',
    )
    @action(detail=True, methods=['get'])
    def move_up(self, request, *args, **kwargs):
        return self._do_actual_move('up', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        responses=ExternalIdpReorderSerializer,
        summary='外部插件下移',
    )
    @action(detail=True, methods=['get'])
    def move_down(self, request, *args, **kwargs):
        return self._do_actual_move('down', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        responses=ExternalIdpReorderSerializer,
        summary='外部插件置顶',
    )
    @action(detail=True, methods=['get'])
    def move_top(self, request, *args, **kwargs):
        return self._do_actual_move('top', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin', 'authfactor.thirdpartylogin'],
        responses=ExternalIdpReorderSerializer,
        summary='外部插件置底',
    )
    @action(detail=True, methods=['get'])
    def move_bottom(self, request, *args, **kwargs):
        return self._do_actual_move('bottom', request, *args, **kwargs)

    def _do_actual_move(self, direction, request, *args, **kwargs):

        assert direction in ('top', 'bottom', 'up', 'down')
        current_uuid = kwargs.get('pk')
        context = self.get_serializer_context()
        tenant = context['tenant']
        order_str = 'order_no' if direction in ('up', 'top') else '-order_no'
        valid_idps = ExternalIdp.valid_objects.filter(tenant=tenant).order_by(order_str)
        index = 0
        current_idp = None
        for i, idp in enumerate(valid_idps):
            if idp.uuid.hex == current_uuid:
                index = i
                current_idp = idp
        if index:
            if direction in ['top', 'bottom']:
                prev_idp = valid_idps[0]
            else:
                prev_idp = valid_idps[index - 1]
            prev_order_no = prev_idp.order_no
            prev_idp.order_no = current_idp.order_no
            current_idp.order_no = prev_order_no
            prev_idp.save()
            current_idp.save()
        return JsonResponse(
            data={
                'error': Code.OK.value,
            }
        )
