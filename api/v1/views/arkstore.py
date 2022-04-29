from rest_framework.generics import GenericAPIView, ListAPIView
from sqlalchemy import extract
from common.paginator import DefaultListPaginator
from api.v1.serializers.arkstore import ArkStoreExtensionSerializer
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from perm.custom_access import ApiAccessPermission
from collections import OrderedDict
from tenant.models import Tenant
from common.code import Code
from common.arkstore import (
    get_arkstore_access_token,
    purcharse_arkstore_extension,
    install_arkstore_extension,
    bind_arkstore_agent,
    get_arkstore_apps_and_extensions,
    get_arkid_saas_app_detail,
)


@extend_schema(
    roles=['globaladmin'],
    tags=['arkstore-extension'],
    summary='获取arkstore插件列表'
)
class ArkStoreAPIView(ListAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ArkStoreExtensionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        page = self.request.query_params.get('page')
        page_size = self.request.query_params.get('page_size')
        # arkstore use offset and limit
        if page and page_size:
            limit = int(page_size)
            offset = (int(page)-1) * int(page_size)
        purchased = self.request.query_params.get('purchased')
        token = self.request.user.token
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        saas_extensions_data = get_arkstore_apps_and_extensions(access_token, purchased, offset, limit)
        saas_extensions_data = saas_extensions_data['items']
        saas_extensions = []
        for extension_data in saas_extensions_data:
            extension = OrderedDict()
            extension['name'] = extension_data['name']
            extension['description'] = extension_data['description']
            extension['version'] = extension_data['version']
            extension['uuid'] = extension_data['uuid']
            extension['logo'] = extension_data['logo']
            extension['maintainer'] = extension_data['author']
            # extension['purchased'] = '已购买' if extension_data['purchased'] == True else '未购买'
            extension['purchased'] = extension_data['purchased']
            if extension_data['upgrade']:
                extension['button'] = '升级'
            elif extension['purchased']:
                extension['button'] = '安装'
            else:
                extension['button'] = '购买'
            extension['tags'] = ''
            extension['type'] = extension_data['type']
            extension['scope'] = ''
            extension['homepage'] = ''
            saas_extensions.append(extension)

        return saas_extensions


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'], summary='arkstore下单')
class ArkStoreOrderView(GenericAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    def post(self, request, tenant_uuid, *args, **kwargs):
        extension_uuid = request.data['extension_uuid']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        resp = purcharse_arkstore_extension(access_token, extension_uuid)
        return JsonResponse(resp)


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'], summary='arkstore下载插件')
class ArkStoreInstallView(GenericAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid, *args, **kwargs):
        extension_uuid = kwargs['pk']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        result = install_arkstore_extension(tenant, token, extension_uuid)
        result = {'error': Code.OK.value}
        return JsonResponse(result)


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'], summary='arkstore下单')
class ArkStoreBindAgentView(GenericAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    def post(self, request, tenant_uuid, *args, **kwargs):
        tenant_slug = request.data['tenant_slug']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        resp = bind_arkstore_agent(access_token, tenant_slug)
        return JsonResponse(resp)


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'], summary='arkstore下单')
class ArkStoreGetAutoFormFillDataView(GenericAPIView):

    permission_classes = [IsAuthenticated, ApiAccessPermission]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid, *args, **kwargs):
        extension_uuid = kwargs['pk']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        result = get_arkid_saas_app_detail(tenant, token, extension_uuid)
        return JsonResponse(result)
