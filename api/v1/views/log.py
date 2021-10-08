import datetime
from re import T
from api.v1.serializers.log import LogSerializer, LogDetailSerializer
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from rest_framework import viewsets
from rest_framework.permissions import DjangoObjectPermissions, IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from log.models import Log
from tenant.models import TenantLogConfig


def get_log_retention_date(tenant):
    tenant = TenantLogConfig.valid_objects.filter(tenant=tenant).first()
    log_retention_period = tenant.data.get('log_retention_period', 30)
    log_retention_date = datetime.datetime.now() - datetime.timedelta(days=log_retention_period)
    return log_retention_date


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log']
)
class UserLogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = LogSerializer
    pagination_class = DefaultListPaginator

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
            'created__gt': get_log_retention_date(tenant),
        }

        log = Log.valid_objects.filter(**kwargs).first()
        return log

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'data__user__admin': False,
            'created__gt': get_log_retention_date(tenant),
        }

        qs = Log.valid_objects.filter(**kwargs).order_by('-id')
        return qs


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log']
)
class AdminLogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = LogSerializer
    pagination_class = DefaultListPaginator

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
            'created__gt': get_log_retention_date(tenant),
        }

        log = Log.valid_objects.filter(**kwargs).first()
        return log

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'data__user__admin': True,
            'created__gt': get_log_retention_date(tenant),
        }

        qs = Log.valid_objects.filter(**kwargs).order_by('-id')
        return qs


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log']
)
class LogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = LogDetailSerializer

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
            'created__gt': get_log_retention_date(tenant),
        }

        log = Log.valid_objects.filter(**kwargs).first()
        return log
