from api.v1.serializers.log import LogSerializer, LogDetailSerializer
from common.paginator import DefaultListPaginator
from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from collections import OrderedDict
from log.models import Log


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags = ['log']
)
class UserLogViewSet(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = LogSerializer
    pagination_class = DefaultListPaginator

    @staticmethod
    def get_log_data(log):
        obj = OrderedDict()
        data = log.data
        obj['uuid'] = log.uuid
        obj['timestamp'] = log.created
        obj['user'] = data['user']['username']
        obj['ip'] = data['ip_address']
        obj['action'] = data['request']['full_path']
        return obj

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        log = Log.valid_objects.filter(**kwargs).first()
        obj = self.get_log_data(log)
        return obj

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'data__user__admin': False,
        }

        logs = Log.valid_objects.filter(**kwargs).order_by('id')
        qs = []
        for log in logs:
            obj = self.get_log_data(log)
            qs.append(obj)
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

    @staticmethod
    def get_log_data(log):
        obj = OrderedDict()
        data = log.data
        obj['uuid'] = log.uuid
        obj['timestamp'] = log.created
        obj['user'] = data['user']['username']
        obj['ip'] = data['ip_address']
        obj['action'] = data['request']['full_path']
        return obj

    def get_object(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'uuid': self.kwargs['pk'],
        }

        log = Log.valid_objects.filter(**kwargs).first()
        obj = self.get_log_data(log)
        return obj

    def get_queryset(self):
        context = self.get_serializer_context()
        tenant = context['tenant']

        kwargs = {
            'tenant': tenant,
            'data__user__admin': True,
        }

        logs = Log.valid_objects.filter(**kwargs).order_by('id')
        qs = []
        for log in logs:
            obj = self.get_log_data(log)
            qs.append(obj)
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
        }

        log = Log.valid_objects.filter(**kwargs).first()
        return log
