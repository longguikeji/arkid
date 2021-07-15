from api.v1.serializers.webhook_trigger_history import WebHookTriggerHistorySerializer
from common.paginator import DefaultListPaginator
from drf_spectacular.utils import extend_schema_view
from openapi.utils import extend_schema
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from tenant.models import Tenant
from webhook.models import WebHook, WebHookTriggerHistory

from .base import BaseViewSet
import requests


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

    @extend_schema(
        roles=['tenant admin', 'global admin'],
    )
    @action(detail=True, methods=['get'])
    def retry(self, request, *args, **kwargs):
        # context = self.get_serializer_context()
        # tenant = context['tenant']
        history = self.get_object()
        if not history:
            return Response(
                {'error': 'No webhook history find'}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            webhook = history.webhook
            url = webhook.url
            data = history.request
            headers = {
                'Arkid-Signature-256': webhook.sign(data),
                'Arkid-Hook-UUID': str(webhook.uuid),
            }
            try:
                res = requests.post(url, data, headers=headers, timeout=3)
            except Exception as exc:
                history.status = 'failed'
                history.response = str(exc)
                history.save()
            else:
                history.status = 'success'
                history.response = {
                    'status_code': res.status_code,
                    'response': res.text,
                }
                history.save()
            return Response(status=status.HTTP_200_OK)
