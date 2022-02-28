from .base import BaseViewSet
from api.v1.serializers.authorization_agent import (
    AuthorizationAgentSerializer,
    AuthorizationAgentListSerializer,
    AuthorizationAgentReorderSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from authorization_agent.models import AuthorizationAgent
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from perm.custom_access import ApiAccessPermission
from common.code import Code

AuthorizationAgentPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='AuthorizationAgentPolymorphicProxySerializer',
    serializers=get_app_runtime().authorization_agent_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin'], summary='删除认证代理'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin']),
)
@extend_schema(tags=['authorization_agent'])
class AuthorizationAgentViewSet(BaseViewSet):

    model = AuthorizationAgent

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = AuthorizationAgentSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
        }

        return AuthorizationAgent.valid_objects.filter(**kwargs).order_by('order_no', 'id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = AuthorizationAgent.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(roles=['tenantadmin', 'globaladmin'], responses=AuthorizationAgentListSerializer, summary='认证代理列表')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=AuthorizationAgentPolymorphicProxySerializer,
        responses=AuthorizationAgentPolymorphicProxySerializer,
        summary='更新认证代理',
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=AuthorizationAgentPolymorphicProxySerializer,
        responses=AuthorizationAgentPolymorphicProxySerializer,
        summary='创建认证代理',
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(roles=['tenantadmin', 'globaladmin'], responses=AuthorizationAgentPolymorphicProxySerializer, summary='获取认证代理')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=AuthorizationAgentReorderSerializer,
        responses=AuthorizationAgentReorderSerializer,
        summary='批量更改认证代理'
    )
    @action(detail=False, methods=['post'])
    def batch_update(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        idp_uuid_list = request.data.get('idps')
        idps = AuthorizationAgent.valid_objects.filter(
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
        roles=['tenantadmin', 'globaladmin'],
        responses=AuthorizationAgentReorderSerializer,
        summary='上移认证代理',
    )
    @action(detail=True, methods=['get'])
    def move_up(self, request, *args, **kwargs):
        return self._do_actual_move('up', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=AuthorizationAgentReorderSerializer,
        summary='下移认证代理',
    )
    @action(detail=True, methods=['get'])
    def move_down(self, request, *args, **kwargs):
        return self._do_actual_move('down', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=AuthorizationAgentReorderSerializer,
        summary='置顶认证代理',
    )
    @action(detail=True, methods=['get'])
    def move_top(self, request, *args, **kwargs):
        return self._do_actual_move('top', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=AuthorizationAgentReorderSerializer,
        summary='置底认证代理',
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
        valid_idps = AuthorizationAgent.valid_objects.filter(tenant=tenant).order_by(order_str)
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
