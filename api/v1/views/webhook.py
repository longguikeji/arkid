
from rest_framework.permissions import IsAuthenticated

# from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from drf_spectacular.utils import extend_schema_view
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from webhook.models import (
    WebHook,
)
from api.v1.serializers.webhook import (
    WebHookSerializer,
    WebHookListResponseSerializer,
    WebhookCreateRequestSerializer,
)
from common.paginator import DefaultListPaginator
# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter


# @extend_schema_view(
#     list=extend_schema(
#         responses=WebHookListResponseSerializer,
#     ),
#     retrieve=extend_schema(
#         responses=WebHookListResponseSerializer,
#     ),
#     create=extend_schema(
#         request=WebhookCreateRequestSerializer,
#     ),
#     update=extend_schema(
#         request=WebhookCreateRequestSerializer,
#     ),
from openapi.utils import extend_schema
from .base import BaseViewSet

@extend_schema_view(
    list=extend_schema(roles=['tenant admin', 'global admin']),
    retrieve=extend_schema(roles=['tenant admin', 'global admin']),
    destroy=extend_schema(roles=['tenant admin', 'global admin']),
    update=extend_schema(roles=['tenant admin', 'global admin']),
    create=extend_schema(roles=['tenant admin', 'global admin']),
    partial_update=extend_schema(roles=['tenant admin', 'global admin']),
)
@extend_schema(
    tags = ['webhook'],
)
class WebHookViewSet(BaseViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

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
