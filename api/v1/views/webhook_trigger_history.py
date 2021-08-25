from api.v1.serializers.webhook_trigger_history import WebhookTriggerHistorySerializer
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
from webhook.models import Webhook, WebhookTriggerHistory
from common.code import Code

from .base import BaseViewSet
import requests
import json


@extend_schema_view(
    list=extend_schema(roles=['tenant admin', 'global admin']),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    destory=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(tags=['webhook_histroy'])
class WebhookTriggerHistoryViewSet(
    NestedViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = WebhookTriggerHistorySerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        query_dict = self.get_parents_query_dict()
        tenant_uuid = query_dict.get('tenant')
        webhook_uuid = query_dict.get('webhook')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        webhook = Webhook.objects.filter(uuid=webhook_uuid).first()
        objs = WebhookTriggerHistory.valid_objects.filter(
            tenant=tenant, webhook=webhook
        ).order_by('-id')
        return objs

    def get_object(self):
        query_dict = self.get_parents_query_dict()
        tenant_uuid = query_dict.get('tenant')
        webhook_uuid = query_dict.get('webhook')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        webhook = Webhook.objects.filter(uuid=webhook_uuid).first()

        kwargs = {
            'tenant': tenant,
            'webhook': webhook,
            'uuid': self.kwargs['pk'],
        }

        obj = WebhookTriggerHistory.valid_objects.filter(**kwargs).first()
        return obj

    @extend_schema(
        roles=['tenant admin', 'global admin'],
    )
    @action(detail=True, methods=['get'])
    def retry(self, request, *args, **kwargs):
        history = self.get_object()
        webhook = history.webhook
        url = webhook.url
        request_data = json.loads(history.request)
        request_headers = request_data.get('headers')
        request_body = request_data.get('body')
        response = None
        try:
            response = requests.post(
                url, request_body, headers=request_headers, timeout=3
            )
            response.raise_for_status()
        except Exception as exc:
            if response:
                status_code = response.status_code
            else:
                status_code = None
            history.status = 'failed'
            response_data = json.dumps({'status_code': status_code, 'body': str(exc)})
            history.response = response_data
            history.save()
        else:
            history.status = 'success'
            history.response = json.dumps(
                {
                    'status_code': response.status_code,
                    'response': response.text,
                }
            )
            history.save()
        return Response(status=status.HTTP_200_OK)
