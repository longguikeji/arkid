from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from webhook.models import (
    WebHookTriggerHistory
)
from api.v1.serializers.webhook_trigger_history import (
    WebHookTriggerHistorySerializer
)
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from .base import BaseViewSet

@extend_schema_view(
    list=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    retrieve=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
)
@extend_schema(
    tags = ['webhook_histroy']
)
class WebHookTriggerHistoryViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    permission_classes = []
    authentication_classes = []

    serializer_class = WebHookTriggerHistorySerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        objs = WebHookTriggerHistory.active_objects.filter(
            tenant=tenant,
        ).order_by('-id')
        return objs

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        obj = WebHookTriggerHistory.valid_objects.filter(**kwargs).first()
        return obj