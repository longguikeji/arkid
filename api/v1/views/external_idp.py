from .base import BaseViewSet
from api.v1.serializers.external_idp import (
    ExternalIdpSerializer,
    ExternalIdpListSerializer,
    ExternalIdpReorderSerializer,
)
from runtime import get_app_runtime
from django.http.response import JsonResponse
from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from common.paginator import DefaultListPaginator
from .base import BaseViewSet
from external_idp.models import ExternalIdp
from rest_framework.decorators import action
from common.code import Code

ExternalIdpPolymorphicProxySerializer = PolymorphicProxySerializer(
    component_name='ExternalIdpPolymorphicProxySerializer',
    serializers=get_app_runtime().external_idp_serializers,
    resource_type_field_name='type',
)


@extend_schema(tags=['external_idp'])
class ExternalIdpViewSet(BaseViewSet):

    model = ExternalIdp

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

    @extend_schema(responses=ExternalIdpListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=ExternalIdpPolymorphicProxySerializer,
        responses=ExternalIdpPolymorphicProxySerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=ExternalIdpPolymorphicProxySerializer,
        responses=ExternalIdpPolymorphicProxySerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(responses=ExternalIdpPolymorphicProxySerializer)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=ExternalIdpReorderSerializer,
        responses=ExternalIdpReorderSerializer,
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
        responses=ExternalIdpReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_up(self, request, *args, **kwargs):
        return self._do_actual_move('up', request, *args, **kwargs)

    @extend_schema(
        responses=ExternalIdpReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_down(self, request, *args, **kwargs):
        return self._do_actual_move('down', request, *args, **kwargs)

    @extend_schema(
        responses=ExternalIdpReorderSerializer,
    )
    @action(detail=True, methods=['get'])
    def move_top(self, request, *args, **kwargs):
        return self._do_actual_move('top', request, *args, **kwargs)

    @extend_schema(
        responses=ExternalIdpReorderSerializer,
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
