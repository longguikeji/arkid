from drf_spectacular.utils import extend_schema
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from .provider import TenantUserConfigIdpProvider
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from openapi.utils import extend_schema
from extension_root.tenantuserconfig.serializers import(
    TenantUserLogOutConfigSerializer, TenantUserConfigFieldSelectListSerializer,
    TenantUserLoggingConfigSerializer, TenantUserTokenConfigSerializer, TenantUserEditFieldListConfigSerializer,
)
from extension_root.tenantuserconfig.models import TenantUserConfig
from inventory.models import CustomField
from tenant.models import Tenant
import copy


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantUserLogOutConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantUserLogOutConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return None

        config = TenantUserConfig.active_objects.filter(
            tenant=tenant
        ).first()
        if config is None:
            config = TenantUserConfig()
            config.save_data(tenant)
        return config
    
    def get(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        serializer = self.get_serializer({
            'is_logout': data.get('is_logout')
        })
        return Response(serializer.data)
    
    def put(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        is_logout = request.data.get('is_logout')
        data['is_logout'] = is_logout
        config.data = data
        config.save()
        serializer = self.get_serializer({
            'is_logout': data.get('is_logout')
        })
        return Response(serializer.data)


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantUserLoggingConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantUserLoggingConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return None
        config = TenantUserConfig.active_objects.filter(
            tenant=tenant
        ).first()
        if config is None:
            config = TenantUserConfig()
            config.save_data(tenant)
        return config
    
    def get(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        serializer = self.get_serializer({
            'is_logging_ip': data.get('is_logging_ip'),
            'is_logging_device': data.get('is_logging_device')
        })
        return Response(serializer.data)
    
    def put(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        is_logging_ip = request.data.get('is_logging_ip', None)
        is_logging_device = request.data.get('is_logging_device', None)
        if is_logging_ip is not None:
            data['is_logging_ip'] = is_logging_ip
        if is_logging_device is not None:
            data['is_logging_device'] = is_logging_device
        config.data = data
        config.save()
        serializer = self.get_serializer({
            'is_logging_ip': data.get('is_logging_ip'),
            'is_logging_device': data.get('is_logging_device')
        })
        return Response(serializer.data)


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantUserTokenConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantUserTokenConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        config = TenantUserConfig.active_objects.filter(
            tenant=tenant
        ).first()
        if config is None:
            config = TenantUserConfig()
            config.save_data(tenant)
        return config
    
    def get(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        serializer = self.get_serializer({
            'is_look_token': data.get('is_look_token'),
            'is_manual_overdue_token': data.get('is_manual_overdue_token')
        })
        return Response(serializer.data)
    
    def put(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        is_look_token = request.data.get('is_look_token', None)
        is_manual_overdue_token = request.data.get('is_manual_overdue_token', None)
        if is_look_token is not None:
            data['is_look_token'] = is_look_token
        if is_manual_overdue_token is not None:
            data['is_manual_overdue_token'] = is_manual_overdue_token
        config.data = data
        config.save()
        serializer = self.get_serializer({
            'is_look_token': data.get('is_look_token'),
            'is_manual_overdue_token': data.get('is_manual_overdue_token')
        })
        return Response(serializer.data)

@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantUserConfigFieldSelectListView(generics.RetrieveUpdateAPIView):

    serializer_class = TenantUserConfigFieldSelectListSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return check_result

        config = TenantUserConfig.active_objects.filter(
            tenant=tenant
        ).first()
        if config is None:
            config = TenantUserConfig()
            config.save_data(tenant)
        return config

    @extend_schema(responses=TenantUserConfigFieldSelectListSerializer)
    def get(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        is_edit_fields = data.get('is_edit_fields')
        en_names = []
        for is_edit_field in is_edit_fields:
            en_name = is_edit_field.get('en_name')
            if en_name not in en_names:
                en_names.append(en_name)
        result = [
            {'name':'昵称' , 'en_name':'nickname', 'type':'string'},
            {'name':'电话' , 'en_name':'mobile', 'type':'string'},
            {'name':'邮箱' , 'en_name':'email', 'type':'string'},
            {'name':'职称' , 'en_name':'job_title', 'type':'string'},
            {'name':'姓' , 'en_name':'first_name', 'type':'string'},
            {'name':'名' , 'en_name':'last_name', 'type':'string'},
            {'name':'国家' , 'en_name':'country', 'type':'string'},
            {'name':'城市' , 'en_name':'city', 'type':'string'}
        ]
        # 自定义字段开始
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        custom_fields = CustomField.valid_objects.filter(
            tenant=tenant,
            subject='user'
        )
        # 自定义字段结束
        for custom_field in custom_fields:
            result.append({
                'name': custom_field.name,
                'en_name': '',
                'type': 'custom_field'
            })


        for item in result:
            en_name = item.get('en_name')
            if en_name in en_names:
                item['is_select'] = True
            else:
                item['is_select'] = False
        serializer = self.get_serializer({
            'results': result
        })
        return Response(serializer.data)
    
    def put(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        result = request.data.get('results')
        item_copys = []
        for item in result:
            is_select = item.get('is_select')
            if is_select is True:
                item_copy = copy.deepcopy(item)
                item_copy.pop('is_select')
                if item_copy not in item_copys:
                    item_copys.append(item_copy)
        data['is_edit_fields'] = item_copys
        config.data = data
        config.save()
        serializer = self.get_serializer({
            'results': result
        })
        return Response(serializer.data)

        
@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantUserEditFieldListConfigView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantUserEditFieldListConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = self.request.user
        check_result = user.check_permission(tenant)
        if not check_result is None:
            return None

        config = TenantUserConfig.active_objects.filter(
            tenant=tenant
        ).first()
        if config is None:
            config = TenantUserConfig()
            config.save_data(tenant)
        return config
    
    def get(self, request, tenant_uuid):
        config = self.get_object()
        data = config.data
        
        serializer = self.get_serializer({
            'results': data.get('is_edit_fields')
        })
        return Response(serializer.data)
