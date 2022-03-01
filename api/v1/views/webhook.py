from rest_framework.permissions import IsAuthenticated

from perm.custom_access import ApiAccessPermission
from drf_spectacular.utils import extend_schema_view
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from webhook.models import (
    Webhook,
)
from api.v1.serializers.webhook import (
    WebhookSerializer,
    # WebhookListResponseSerializer,
    # WebhookCreateRequestSerializer,
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook列表'),
    retrieve=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook详情'),
    destroy=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook删除'),
    update=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook修改'),
    create=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook创建'),
    partial_update=extend_schema(roles=['tenantadmin', 'globaladmin', 'expansionable.webhook'], summary='webhook更新'),
)
@extend_schema(
    tags=['webhook'],
)
class WebhookViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = WebhookSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        objs = Webhook.active_objects.filter(
            tenant=tenant,
        ).order_by('id')

        return objs

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = Webhook.valid_objects.filter(**kwargs).first()
        return obj
    
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        return super().create(request, *args, **kwargs)