from .base import BaseViewSet, BaseTenantViewSet
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from common.paginator import DefaultListPaginator
from common.extension import InMemExtension
from extension.models import Extension
from extension.utils import find_available_extensions
from api.v1.serializers.market_extension import MarketPlaceExtensionSerializer, MarketPlaceExtensionTagsSerializer
from rest_framework.decorators import action
from openapi.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from rest_framework import generics
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from django.conf import settings
from collections import OrderedDict
import requests
from tenant.models import Tenant


@extend_schema(
    roles=['global admin'],
    tags=['arkstore-extension'],
)
class ArkStoreAPIView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = MarketPlaceExtensionSerializer
    pagination_class = DefaultListPaginator

    def get(self, request, tenant_uuid, *args, **kwargs):
        purchased = self.request.query_params.get('purchased')

        token = self.request.user.token
        tenant = Tenant.objects.get(uuid=tenant_uuid)
        access_token = self.get_arkstore_access_token(tenant, token)
        saas_extensions_data = self.get_arkstore_extensions(access_token, purchased)
        saas_extensions = []
        for extension_data in saas_extensions_data:
            extension = OrderedDict()
            extension.name = extension_data['name']
            extension.description = extension_data['description']
            extension.version = extension_data['version']
            extension.uuid = extension_data['uuid']
            extension.logo = extension_data['logo']
            extension.maintainer = extension_data['author']
            extension.purchased = '已购买' if extension_data['purchased'] == True else '未购买'
            extension.tags = ''
            extension.type = extension.name
            extension.scope = ''
            extension.homepage = ''
            saas_extensions.append(extension)

        return saas_extensions

    # def get_object(self):
    #     ext: InMemExtension
    #     extensions = find_available_extensions()
    #     for ext in extensions:
    #         if ext.name == self.kwargs['pk']:
    #             return ext

    #     return None

    def get_arkstore_extensions(self, access_token, purchased=None):
        arkstore_extensions_url = settings.ARKSTOER_URL + '/api/v1/arkstore/extensions'
        params = {}
        if purchased is not None:
            params['purchased'] = purchased
        resp = requests.get(arkstore_extensions_url, params=params).json()
        return resp


    def get_saas_token(self, tenant, token):
        """
        获取saas平台token
        """
        import requests
        from app.models import App
        app = App.active_objects.filter(name='saas-oidc', tenant=tenant).first()
        data = app.data
        url = data["authorize"]
        params = {
            "client_id": data["client_id"],
            "redirect_uri": data["redirect_uris"],
            "scope": "openid",
            "response_type": "code",
            "token": token,
        }
        resp = requests.get(url, params=params).json()
        return resp['token'], resp['tenant_uuid'], resp['tenant_slug']


    def get_arkstore_access_token(self, tenant, token):
        """
        获取插件商店access_token
        """
        import requests
        saas_token, saas_tenant_uuid, saas_tenant_slug = self.get_saas_token(tenant, token)
        params = {'state': 'client', 'tenant_slug': saas_tenant_slug, 'token': saas_token}
        app_login_url = settings.ARKSTOER_URL + '/api/v1/login'
        resp = requests.get(app_login_url, params=params)
        return resp['access_token']


@extend_schema(roles=['global admin'], tags=['market-extension'])
class MarketOrder(generics.GenericAPIView):

    serializer_class = MarketPlaceExtensionTagsSerializer

    def post(self, request):
        order_url = settings.ARKSTOER_URL + '/api/v1/orders'
        params = {
            # 'price_uuid': ''
            'tenant_uuid': '',
        }
        resp = request.post(order_url, json=params)
        return JsonResponse(resp)


