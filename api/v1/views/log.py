import datetime
import pytz
from re import T
from api.v1.serializers.log import LogSerializer, LogDetailSerializer
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets
from rest_framework.permissions import DjangoObjectPermissions, IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from log.models import Log
from tenant.models import TenantLogConfig
from django.utils.dateparse import parse_datetime


def get_log_retention_date(tenant):
    tenant = TenantLogConfig.valid_objects.filter(tenant=tenant).first()
    if tenant:
        log_retention_period = tenant.data.get('log_retention_period', 30)
    else:
        log_retention_period = 30
    log_retention_date = datetime.datetime.now() - datetime.timedelta(days=log_retention_period)
    return log_retention_date


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log'],
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='ip',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='start',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='end',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
    ],
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
            'created__gte': get_log_retention_date(tenant),
        }

        log = Log.valid_objects.filter(**kwargs).first()
        return log

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']
        username = self.request.query_params.get('username', '')
        ip = self.request.query_params.get('ip', '')
        status = self.request.query_params.get('status', '')
        start = self.request.query_params.get('start', '')
        end = self.request.query_params.get('end', '')

        kwargs = {
            'tenant': tenant,
            'data__user__admin': False,
            'created__gte': get_log_retention_date(tenant),
        }
        if username:
            kwargs['data__user__username'] = username
        if ip:
            kwargs['data__ip_address'] = ip
        if status:
            kwargs['data__response__status_code'] = int(status)
        if start:
            start_time = parse_datetime(start)
            if start_time:
                kwargs['created__gte'] = start_time
        if end:
            end_time = parse_datetime(end)
            if end_time:
                kwargs['created__lte'] = end_time

        qs = Log.valid_objects.filter(**kwargs).order_by('-id')
        return qs


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log'],
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='ip',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='status',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='start',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name='end',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
    ],
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
        username = self.request.query_params.get('username', '')
        ip = self.request.query_params.get('ip', '')
        status = self.request.query_params.get('status', '')
        start = self.request.query_params.get('start', '')
        end = self.request.query_params.get('end', '')

        kwargs = {
            'tenant': tenant,
            'data__user__admin': True,
            'created__gte': get_log_retention_date(tenant),
        }
        if username:
            kwargs['data__user__username'] = username
        if ip:
            kwargs['data__ip_address'] = ip
        if status:
            kwargs['data__response__status_code'] = int(status)
        if start:
            start_time = parse_datetime(start)
            if start_time:
                kwargs['created__gte'] = start_time
        if end:
            end_time = parse_datetime(end)
            if end_time:
                kwargs['created__lte'] = end_time

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
