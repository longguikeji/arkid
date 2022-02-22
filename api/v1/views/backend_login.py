from .base import BaseViewSet
from api.v1.serializers.backend_login import (
    BackendLoginSerializer,
    BackendLoginListSerializer,
    BackendLoginReorderSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from openapi.utils import extend_schema
from drf_spectacular.utils import PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from backend_login.models import BackendLogin 
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from common.code import Code

BackendLoginPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='BackendLoginPolymorphicProxySerializer',
    serializers=get_app_runtime().backend_login_serializers,
    resource_type_field_name='type',
)


@extend_schema_view(
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin']),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin']),
)
@extend_schema(tags=['backend_login'])
class BackendLoginViewSet(BaseViewSet):

    model = BackendLogin 

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = BackendLoginSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return []

        kwargs = {
            'tenant': tenant,
        }

        return BackendLogin.valid_objects.filter(**kwargs).order_by('order_no', 'id')

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = BackendLogin.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(roles=['tenantadmin', 'globaladmin'], responses=BackendLoginListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=BackendLoginPolymorphicProxySerializer,
        responses=BackendLoginPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=BackendLoginPolymorphicProxySerializer,
        responses=BackendLoginPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(roles=['tenantadmin', 'globaladmin'], responses=BackendLoginPolymorphicProxySerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        request=BackendLoginReorderSerializer,
        responses=BackendLoginReorderSerializer,
    )
    @action(detail=False, methods=['post'])
    def batch_update(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        tenant = context['tenant']
        backend_login_uuid_list = request.data.get('backend_logins')
        backend_logins = BackendLogin.valid_objects.filter(
            uuid__in=backend_login_uuid_list, tenant=tenant
        ).order_by('order_no')
        original_order_no = [backend.order_no for backend in backend_logins]
        index = 0
        for uuid in backend_login_uuid_list:
            backend = backend_logins.filter(uuid=uuid).first()
            if not backend:
                continue
            backend.order_no = original_order_no[index]
            backend.save()
            index += 1
        return JsonResponse(
            data={
                'error': Code.OK.value,
            }
        )

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=BackendLoginReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_up(self, request, *args, **kwargs):
        return self._do_actual_move('up', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=BackendLoginReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_down(self, request, *args, **kwargs):
        return self._do_actual_move('down', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=BackendLoginReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_top(self, request, *args, **kwargs):
        return self._do_actual_move('top', request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        responses=BackendLoginReorderSerializer,
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
        valid_logins = BackendLogin.valid_objects.filter(tenant=tenant).order_by(order_str)
        index = 0
        current_login = None
        for i, login in enumerate(valid_logins):
            if login.uuid.hex == current_uuid:
                index = i
                current_login = login 
        if index:
            if direction in ['top', 'bottom']:
                prev_login = valid_logins[0]
            else:
                prev_login = valid_logins[index - 1]
            prev_order_no = prev_login.order_no
            prev_login.order_no = current_login.order_no
            current_login.order_no = prev_order_no
            prev_login.save()
            current_login.save()
        return JsonResponse(
            data={
                'error': Code.OK.value,
            }
        )
