from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
# from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from webhook.models import (
    WebHook,
)
from api.v1.serializers.webhook import (
    WebHookSerializer
)
from common.paginator import DefaultListPaginator
from drf_spectacular.utils import extend_schema
from .base import BaseViewSet

@extend_schema(
    tags = ['webhook']
)
class WebHookViewSet(BaseViewSet):

    # permission_classes = [IsAuthenticated]
    # authentication_classes = [ExpiringTokenAuthentication]

    permission_classes = []
    authentication_classes = []

    serializer_class = WebHookSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        objs = WebHook.active_objects.filter(
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

        obj = WebHook.valid_objects.filter(**kwargs).first()
        return obj