from api.v1.serializers.webhook_trigger_history import WebHookTriggerHistorySerializer
from common.paginator import DefaultListPaginator
from drf_spectacular.utils import extend_schema_view
from openapi.utils import extend_schema
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework_extensions.mixins import NestedViewSetMixin

from tenant.models import Tenant
from webhook.models import WebHook, WebHookTriggerHistory

from .base import BaseViewSet


@extend_schema_view(
    list=extend_schema(roles=['tenant admin', 'global admin']),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    destory=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(tags=['webhook_histroy'])
class WebHookTriggerHistoryViewSet(
    NestedViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = WebHookTriggerHistorySerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        query_dict = self.get_parents_query_dict()
        tenant_uuid = query_dict.get('tenant')
        webhook_uuid = query_dict.get('webhook')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        webhook = WebHook.objects.filter(uuid=webhook_uuid).first()
        objs = WebHookTriggerHistory.valid_objects.filter(
            tenant=tenant, webhook=webhook
        ).order_by('-id')
        return objs

    def get_object(self):
        query_dict = self.get_parents_query_dict()
        tenant_uuid = query_dict.get('tenant')
        webhook_uuid = query_dict.get('webhook')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        webhook = WebHook.objects.filter(uuid=webhook_uuid).first()

        kwargs = {
            'tenant': tenant,
            'webhook': webhook,
            'uuid': self.kwargs['pk'],
        }

        obj = WebHookTriggerHistory.valid_objects.filter(**kwargs).first()
        return obj
