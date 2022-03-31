import os
import base64
import json
import requests
import datetime
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from .user_info_manager import ArkIDUserInfoManager, APICallError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from urllib.parse import urlencode, unquote
import urllib.parse
from django.db.models import Max
from django.urls import reverse
from django.db import transaction
from config import get_app_config
from tenant.models import Tenant
from drf_spectacular.utils import extend_schema
from .provider import ArkIDSaasIdpProvider
from inventory.models import User, Permission
from runtime import get_app_runtime, Runtime
from common.provider import ExternalIdpProvider
from .models import LocalSaasArkIDBind
from external_idp.models import ExternalIdp

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


@extend_schema(tags=["arkid"])
class ArkIDLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        # @TODO: keep other query params

        provider = ArkIDSaasIdpProvider()
        provider.load_data(tenant_uuid=tenant_uuid)

        next_url = request.GET.get("next", "")
        state_data = json.dumps({'next_url': next_url})
        state = base64.urlsafe_b64encode(state_data.encode()).decode()
        redirect_uri = urllib.parse.quote(provider.callback_url)

        url = "{}?client_id={}&redirect_uri={}&response_type=code&scope={}&state={}".format(
            provider.authorize_url,
            provider.client_id,
            redirect_uri,
            provider.scope,
            state,
        )
        return HttpResponseRedirect(url)


@extend_schema(tags=["arkid"])
class ArkIDCallbackView(APIView):

    permission_classes = []
    authentication_classes = []

    def get(self, request, tenant_uuid):
        """
        处理arkid用户登录之后重定向页面
        """
        code = request.GET["code"]
        state = request.GET.get("state", None)
        next_url = None
        if state:
            state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
            next_url = state_data.get('next_url')

        # frontend_host = get_app_config().get_frontend_host().replace('http://' , '').replace('https://' , '')
        # if "third_part_callback" not in next_url or frontend_host not in next_url:
        #     return Response({'error_msg': '错误的跳转页面'}, HTTP_200_OK)

        if code:
            try:
                provider = ArkIDSaasIdpProvider()
                provider.load_data(tenant_uuid=tenant_uuid)
                user_info = ArkIDUserInfoManager(
                    provider,
                    tenant_uuid,
                ).get_user_info(code)
            except APICallError as error:
                raise ValidationError({"code": ["invalid"], "message": error})
        else:
            raise ValidationError({"code": ["required"]})

        user = self.update_or_create_user(user_info, tenant_uuid)
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        context = {
            "token": user.token,
            "tenant_uuid": tenant_uuid,
            "tenant_slug": tenant.slug,
        }
        if next_url:
            if '&next=' in next_url:
                frontend_url, next_redirect_url = next_url.split('&next=', 1)
            else:
                frontend_url, next_redirect_url = next_url, ''
            if next_redirect_url:
                context['next'] = urllib.parse.quote(next_redirect_url)
            query_string = urlencode(context)
            url = f"{frontend_url}?{query_string}"
            url = unquote(url)
            return HttpResponseRedirect(url)

        return Response(context, HTTP_200_OK)

    @transaction.atomic()
    def update_or_create_user(self, user_info, tenant_uuid):
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        user_attrs_map = {
            'preferred_username': 'username',
            # 'sub_uuid': 'user_uuid',
            'family_name': 'first_name',
            'given_name': 'last_name',
            'nickname': 'nickname',
            'phone_number': 'mobile',
            'picture': 'picture',
            'groups': 'groups',
        }
        user_attrs = {}
        for k,v in user_attrs_map.items():
            if k in user_info:
                user_attrs[v] = user_info.get(k, '')

        # groups 包含用户所有角色
        groups = user_attrs.pop('groups', [])

        # username 避免不同租户冲突
        username = user_attrs.pop('username')
        username = f"{username}_{tenant_uuid}"

        user, created = User.objects.update_or_create(username=username, defaults=user_attrs)
        if created:
            user.set_unusable_password()
        user.tenants.add(tenant)
        user.last_login = datetime.datetime.now()

        if 'tenant_admin' in groups:
            permission = Permission.active_objects.filter(
                is_system_permission=True, codename=tenant.admin_perm_code
            ).first()
            if permission:
                user.user_permissions.add(permission)

        user.save()

        return user


@extend_schema(tags=["arkid"])
class ArkIDBindAPIView(APIView):

    permission_classes = []
    authentication_classes = []

    # serializer_class = ArkIDBindSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        """
        输入：公司名，联系人，邮箱，手机号
        本地 arkid 绑定 saas arkid 租户
        """
        data = request.data
        
        local_tenant_uuid = data['local_tenant_uuid']
        local_tenant_slug = data['local_tenant_slug']
        local_host = data['local_host']
        company_name = data['company_name']
        contact_person = data['contact_person']
        email = data['email']
        mobile = data['mobile']
        client_id = data['client_id']
        client_secret = data['client_secret']
        saas_tenant_slug = data['saas_tenant_slug']

        if Tenant.objects.filter(slug=saas_tenant_slug).exists():
            data = {'error': f'{saas_tenant_slug} conflict'}
            return Response(data, HTTP_200_OK)

        kwargs = {'name': company_name, 'slug': saas_tenant_slug}
        saas_tenant = Tenant.objects.create(**kwargs)

        LocalSaasArkIDBind.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            mobile=mobile,
            saas_tenant=saas_tenant,
            local_tenant_uuid=local_tenant_uuid,
            local_tenant_slug=local_tenant_slug,
            local_host=local_host,
        )

        # create arkid-saas login
        external_idp, _ = ExternalIdp.objects.get_or_create(
            tenant=saas_tenant,
            type='arkid_saas',
        )
        external_idp.is_del = False
        external_idp.is_active = True

        if not external_idp.order_no:
            max_order_no = (
                ExternalIdp.objects.filter(tenant=saas_tenant)
                .aggregate(Max('order_no'))
                .get('order_no__max')
            )
            external_idp.order_no = max_order_no + 1

        # reverse failed ??
        # oauth_server_url = local_host + \
        #     reverse(
        #         "api:oauth2_authorization_server:oidc-connect-discovery-info",
        #         args=[local_tenant_uuid]
        #     )
        # oauth_server_url = local_host + \
        #         f'/api/v1/tenant/{local_tenant_uuid}/.well-known/openid-configuration'
        # resp = requests.get(oauth_server_url).json()
        # authorize_url = resp["authorization_endpoint"]
        # token_url = resp["token_endpoint"]
        # userinfo_url = resp["userinfo_endpoint"]

        authorize_url = f"{local_host}/api/v1/tenant/{local_tenant_uuid}/oauth/authorize/"
        token_url = f"{local_host}/api/v1/tenant/{local_tenant_uuid}/oauth/token/"
        userinfo_url = f"{local_host}/api/v1/tenant/{local_tenant_uuid}/oauth/userinfo/"

        # reverse failed ??
        # callback_url = saas_host+reverse("api:arkid_saas:callback", args=[saas_tenant.uuid])
        saas_host = get_app_config().get_frontend_host()
        callback_url = f'{saas_host}/api/v1/tenant/{saas_tenant.uuid}/arkid/saas/callback'
        login_url = f'{saas_host}/api/v1/tenant/{saas_tenant.uuid}/arkid/saas/login'
        idp_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'authorize_url': authorize_url,
            'token_url': token_url,
            'userinfo_url': userinfo_url,
            'login_url': login_url,
            'callback_url': callback_url,
        }

        r: Runtime = get_app_runtime()
        provider_cls: ExternalIdpProvider = r.external_idp_providers.get(
            'arkid_saas', None
        )
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.create(idp_data)
        if data is not None:
            external_idp.data = data
        external_idp.save()

        output = {
            'saas_tenant_uuid':  str(saas_tenant.uuid),
            'saas_tenant_slug': saas_tenant.slug,
            'callback_url': callback_url,
        }
        return Response(output, HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        查询绑定信息
        """
        local_tenant_uuid = request.query_params['local_tenant_uuid']
        bind = LocalSaasArkIDBind.active_objects.filter(local_tenant_uuid=local_tenant_uuid).first()
        if not bind:
            data = {'error': '未绑定'}
            return Response(data, HTTP_200_OK)

        saas_tenant_url = get_app_config().get_slug_frontend_host(bind.saas_tenant.slug)
        data = {
            'company_name': bind.company_name,
            'contact_person': bind.contact_person,
            'email': bind.email,
            'mobile': bind.mobile,
            'local_tenant_uuid': bind.local_tenant_uuid,
            'local_tenant_slug': bind.local_tenant_slug,
            'saas_tenant_slug': bind.saas_tenant.slug,
            'saas_tenant_uuid': str(bind.saas_tenant.uuid),
            'saas_tenant_url': saas_tenant_url,
        }
        return Response(data, HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        更新绑定信息
        """
        data = request.data
        
        local_tenant_uuid = data['local_tenant_uuid']
        company_name = data['company_name']
        contact_person = data['contact_person']
        email = data['email']
        mobile = data['mobile']

        bind = LocalSaasArkIDBind.active_objects.filter(local_tenant_uuid=local_tenant_uuid).first()
        if not bind:
            data = {'error': '未绑定'}
            return Response(data, HTTP_200_OK)

        bind.company_name = company_name
        bind.contact_person = contact_person
        bind.email = email
        bind.mobile = mobile
        bind.save()
        
        saas_tenant_url = get_app_config().get_slug_frontend_host(bind.saas_tenant.slug)
        data = {
            'company_name': bind.company_name,
            'contact_person': bind.contact_person,
            'email': bind.email,
            'mobile': bind.mobile,
            'local_tenant_uuid': bind.local_tenant_uuid,
            'local_tenant_slug': bind.local_tenant_slug,
            'saas_tenant_slug': bind.saas_tenant.slug,
            'saas_tenant_uuid': str(bind.saas_tenant.uuid),
            'saas_tenant_url': saas_tenant_url,
        }
        return Response(data, HTTP_200_OK)

@extend_schema(tags=["arkid"])
class ArkIDUnBindView(GenericAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def post(self, request, *args, **kwargs):
        """
        解除绑定用户
        """
        local_tenant_uuid = request.data['local_tenant_uuid']
        saas_tenant_uuid = request.data['saas_tenant_uuid']
        saas_tenant = Tenant.objects.filter(uuid=saas_tenant_uuid).first()
        bind = LocalSaasArkIDBind.valid_objects.filter(
            local_tenant_uuid=local_tenant_uuid,
            saas_tenant=saas_tenant
        ).first()
        if bind:
            bind.kill()
            external_idp = ExternalIdp.objects.filter(
                tenant=saas_tenant,
                type='arkid_saas',
            ).first()
            if external_idp:
                external_idp.kill()
            data = {"is_del": True}
        else:
            data = {"is_del": False}
        return Response(data, HTTP_200_OK)
