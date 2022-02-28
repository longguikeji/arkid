import datetime
import pytz
from re import T
from api.v1.serializers.log import LogSerializer, LogDetailSerializer
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from perm.custom_access import ApiAccessPermission
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
    roles=['tenantadmin', 'globaladmin'],
    tags = ['log'],
)
class UserLogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
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
        username = self.request.query_params.get('user', '')
        ip = self.request.query_params.get('ip', '')
        status = self.request.query_params.get('status_code', '')
        start = self.request.query_params.get('time_begin', '')
        end = self.request.query_params.get('time_end', '')

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
        roles=['tenantadmin', 'globaladmin'],
        parameters=[
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='用户',
                required=False,
            ),
            OpenApiParameter(
                name='ip',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='ip地址',
                required=False,
            ),
            OpenApiParameter(
                name='status_code',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='状态码',
                required=False,
            ),
            OpenApiParameter(
                name='time_begin',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='开始时间',
                required=False,
            ),
            OpenApiParameter(
                name='time_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='结束时间',
                required=False,
            ),
        ],
        summary='租户用户日志列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户用户日志详情'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags = ['log'],
)
class AdminLogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
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
        username = self.request.query_params.get('user', '')
        ip = self.request.query_params.get('ip', '')
        status = self.request.query_params.get('status_code', '')
        start = self.request.query_params.get('time_begin', '')
        end = self.request.query_params.get('time_end', '')

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
        roles=['tenantadmin', 'globaladmin'],
        parameters=[
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='用户',
                required=False,
            ),
            OpenApiParameter(
                name='ip',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='ip地址',
                required=False,
            ),
            OpenApiParameter(
                name='status_code',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='状态码',
                required=False,
            ),
            OpenApiParameter(
                name='time_begin',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='开始时间',
                required=False,
            ),
            OpenApiParameter(
                name='time_end',
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
                description='结束时间',
                required=False,
            ),
        ],
        summary='租户管理员日志列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户管理员日志详情'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(
    roles=['tenantadmin', 'globaladmin'],
    tags = ['log']
)
class LogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
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

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户日志列表'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        roles=['tenantadmin', 'globaladmin'],
        summary='租户日志详情'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)