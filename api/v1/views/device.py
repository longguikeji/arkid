from rest_framework import generics
from openapi.utils import extend_schema
from api.v1.serializers.device import (
    DeviceSerializer,
)
from device.models import (
    Device,
)
from device.resouces import (
    DeviceResource,
)
from inventory.models import User, Permission
from tenant.models import Tenant
from common.paginator import DefaultListPaginator
from drf_spectacular.openapi import OpenApiTypes
from django.http.response import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

import datetime


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class DeviceListView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = DeviceSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        tenant_uuid = self.request.query_params.get('tenant_uuid', None)
        device_type = self.request.query_params.get('device_type', None)
        system_version = self.request.query_params.get('system_version', None)
        browser_version = self.request.query_params.get('browser_version', None)
        ip = self.request.query_params.get('ip', None)
        mac_address = self.request.query_params.get('mac_address', None)
        device_number = self.request.query_params.get('device_number', None)
        device_id = self.request.query_params.get('device_id', None)
        account_id = self.request.query_params.get('account_id', None)
        kwargs = {
        }
        if device_type is not None:
            kwargs['device_type'] = device_type
        if system_version is not None:
            kwargs['system_version'] = system_version
        if browser_version is not None:
            kwargs['browser_version'] = browser_version
        if ip is not None:
            kwargs['ip'] = ip
        if mac_address is not None:
            kwargs['mac_address'] = mac_address
        if device_number is not None:
            kwargs['device_number'] = device_number
        if device_id is not None:
            kwargs['device_id'] = device_id
        devices = Device.active_objects.filter(**kwargs)
        if account_id is not None:
            uuids = []
            for device in devices:
                account_ids = device.account_ids
                if account_id in account_ids:
                    uuids.append(device.uuid)
            devices = devices.filter(uuid__in=uuids)
        if tenant_uuid is not None:
            uuids = []
            user_uuids = []
            users = User.active_objects.filter(tenants__uuid=tenant_uuid)
            # 租户管理员的
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
            permission = Permission.active_objects.filter(codename=tenant.admin_perm_code).first()
            manage_users = permission.user_permission_set.all()
            for user in users:
                user_uuids.append(str(user.uuid))
            for manage_user in manage_users:
                user_uuids.append(str(manage_user.uuid))
            for user_uuid in user_uuids:
                for device in devices:
                    account_ids = device.account_ids
                    if user_uuid in account_ids:
                        uuids.append(device.uuid)
                        break
            devices = devices.filter(uuid__in=uuids)
        return devices.order_by('-id')


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['tenant'])
class DeviceDetailView(generics.RetrieveDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = DeviceSerializer

    def get_object(self):
        device_uuid = self.kwargs['device_uuid']
        device = Device.active_objects.filter(uuid=device_uuid).first()
        return device


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['tenant'], responses={(200, 'application/octet-stream'): OpenApiTypes.BINARY})
class DeviceExportView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]
    serializer_class = DeviceSerializer

    def get(self, request):
        tenant_uuid = self.request.query_params.get('tenant_uuid', None)
        device_type = self.request.query_params.get('device_type', None)
        system_version = self.request.query_params.get('system_version', None)
        browser_version = self.request.query_params.get('browser_version', None)
        ip = self.request.query_params.get('ip', None)
        mac_address = self.request.query_params.get('mac_address', None)
        device_number = self.request.query_params.get('device_number', None)
        device_id = self.request.query_params.get('device_id', None)
        account_id = self.request.query_params.get('account_id', None)
        kwargs = {
        }
        if device_type is not None:
            kwargs['device_type'] = device_type
        if system_version is not None:
            kwargs['system_version'] = system_version
        if browser_version is not None:
            kwargs['browser_version'] = browser_version
        if ip is not None:
            kwargs['ip'] = ip
        if mac_address is not None:
            kwargs['mac_address'] = mac_address
        if device_number is not None:
            kwargs['device_number'] = device_number
        if device_id is not None:
            kwargs['device_id'] = device_id
        devices = Device.active_objects.filter(**kwargs)
        if account_id is not None:
            uuids = []
            for device in devices:
                account_ids = device.account_ids
                if account_id in account_ids:
                    uuids.append(device.uuid)
            devices = devices.filter(uuid__in=uuids)
        if tenant_uuid is not None:
            uuids = []
            user_uuids = []
            users = User.valid_objects.filter(tenants__uuid=tenant_uuid)
            for user in users:
                user_uuids.append(str(user.uuid))
            for user_uuid in user_uuids:
                for device in devices:
                    account_ids = device.account_ids
                    if user_uuid in account_ids:
                        uuids.append(device.uuid)
                        break
            devices = devices.filter(uuid__in=uuids)
        devices = devices.order_by('-id')
        # 导出
        data = DeviceResource().export(devices)
        export_data = data.csv
        content_type = 'application/octet-stream'
        response = HttpResponse(export_data, content_type=content_type)
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        filename = '%s-%s.%s' % ('Device', date_str, 'csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
        return response
