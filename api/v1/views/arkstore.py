from rest_framework.generics import GenericAPIView, ListAPIView
from sqlalchemy import extract
from common.paginator import DefaultListPaginator
from api.v1.serializers.arkstore import ArkStoreExtensionSerializer
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.conf import settings
from collections import OrderedDict
import requests
from tenant.models import Tenant
from app.models import App


@extend_schema(
    roles=['globaladmin'],
    tags=['arkstore-extension'],
)
class ArkStoreAPIView(ListAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = ArkStoreExtensionSerializer
    pagination_class = DefaultListPaginator

    def get_queryset(self):
        purchased = self.request.query_params.get('purchased')
        token = self.request.user.token
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        saas_extensions_data = get_arkstore_extensions(access_token, purchased)
        # saas_extensions = []
        # for extension_data in saas_extensions_data:
        #     extension = OrderedDict()
        #     extension.name = extension_data['name']
        #     extension.description = extension_data['description']
        #     extension.version = extension_data['version']
        #     extension.uuid = extension_data['uuid']
        #     extension.logo = extension_data['logo']
        #     extension.maintainer = extension_data['author']
        #     extension.purchased = '已购买' if extension_data['purchased'] == True else '未购买'
        #     extension.tags = ''
        #     extension.type = extension.name
        #     extension.scope = ''
        #     extension.homepage = ''
        #     saas_extensions.append(extension)

        # return saas_extensions
        return saas_extensions_data


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'])
class ArkStoreOrderView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def post(self, request, tenant_uuid, *args, **kwargs):
        extension_uuid = request.data['extension_uuid']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        resp = purcharse_arkstore_extension(access_token, extension_uuid)
        return JsonResponse(resp)


@extend_schema(roles=['globaladmin'], tags=['arkstore-extension'])
class ArkStoreDownloadView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, tenant_uuid, *args, **kwargs):
        extension_uuid = kwargs['pk']
        token = request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = get_arkstore_access_token(tenant, token)
        result = download_arkstore_extension(access_token, extension_uuid)
        return JsonResponse(result)


def get_saas_token(tenant, token):
    """
    获取saas平台token
    """
    app = App.active_objects.filter(name='arkid_saas', tenant=tenant).first()
    data = app.data
    url = data["authorize"]
    params = {
        "client_id": data["client_id"],
        "redirect_uri": data["redirect_uris"],
        "scope": "openid",
        "response_type": "code",
        "token": token,
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_saas_token: {resp.status_code}')
    resp = resp.json()
    return resp['token'], resp['tenant_uuid'], resp['tenant_slug']


def get_arkstore_access_token(tenant, token):
    """
    获取插件商店access_token
    """
    saas_token, saas_tenant_uuid, saas_tenant_slug = get_saas_token(tenant, token)
    params = {'state': 'client', 'tenant_slug': saas_tenant_slug, 'token': saas_token}
    app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
    resp = requests.get(app_login_url, params=params)
    if resp.status_code != 200:
        raise Exception(f'Error get_arkstore_access_token: {resp.status_code}')
    resp = resp.json()
    return resp['access_token']


def get_arkstore_extensions(access_token, purchased=None):
    arkstore_extensions_url = settings.ARKSTOER_URL + '/api/v1/arkstore/extensions'
    headers = {'Authorization': f'Token {access_token}'}
    params = {}
    if purchased is not None:
        params['purchased'] = purchased
    resp = requests.get(arkstore_extensions_url, params=params, headers=headers).json()
    return resp


def purcharse_arkstore_extension(access_token, extension_uuid):
    order_url = settings.ARKSTOER_URL + '/api/v1/orders'
    headers = {'Authorization': f'Token {access_token}'}
    params = {
        'extension_uuid': extension_uuid
    }
    resp = requests.post(order_url, json=params, headers=headers).json()
    return resp


def download_arkstore_extension(access_token, extension_uuid):
    import config
    from pathlib import Path

    ext_detail_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_uuid}'
    headers = {'Authorization': f'Token {access_token}'}
    resp = requests.get(ext_detail_url, headers=headers)
    if resp.status_code != 200:
        return 'failed'
    extension_name = resp.json()['name']

    app_config = config.get_app_config()
    extension_root = app_config.extension.root

    download_url = settings.ARKSTOER_URL + f'/api/v1/arkstore/extensions/{extension_uuid}/download'
    headers = {'Authorization': f'Token {access_token}'}
    resp = requests.get(download_url, headers=headers)
    if resp.status_code != 200:
        return {'error': 'download failed'}

    # delete extension folder
    folder_name = Path(extension_root) / extension_name
    import shutil
    if folder_name.exists():
        try:
            shutil.rmtree(folder_name)
        except OSError as e:
            print ("Error remove folder: %s - %s." % (e.filename, e.strerror))
            return {'error': 'delete extension fodler failed'}

    # unzip
    import zipfile
    import io
    extract_folder = Path(extension_root)
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zip_ref:
        zip_ref.extractall(extract_folder)

    return {'success': 'true'}
