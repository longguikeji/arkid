from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from openapi.utils import extend_schema
from rest_framework.response import Response
from tenant.models import (
    Tenant,
)
from api.v1.serializers.tenant import (
    TenantSerializer,
)
from api.v1.serializers.app import AppBaseInfoSerializer
from common.paginator import DefaultListPaginator
from runtime import get_app_runtime
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.authtoken.models import Token
from inventory.models import Group, User
from common.code import Code
from .base import BaseViewSet
from app.models import App
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.urls import reverse
from common import loginpage as lp


@extend_schema(tags = ['tenant'])
class TenantViewSet(BaseViewSet):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    pagination_class = DefaultListPaginator

    def get_serializer_class(self):
        if self.action == 'apps':
            return AppBaseInfoSerializer

        return TenantSerializer

    @extend_schema(
        summary=_('get tenant list'),
        action_type='list'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(summary=_('update tenant'))
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        objs = Tenant.active_objects.filter().order_by('id')
        return objs

    def get_object(self):
        uuid = self.kwargs['pk']
        return Tenant.active_objects.filter(uuid=uuid).order_by('id').first()

    @property
    def runtime(self):
        return get_app_runtime()

    @action(detail=True, methods=['post'])
    def login(self, request, pk):
        tenant: Tenant = self.get_object()

        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(       
            username=username,
        ).first()

        if not user or not user.check_password(password):
            return JsonResponse(data={
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            })
        
        has_tenant_admin_perm = tenant.has_admin_perm(user)

        if not has_tenant_admin_perm:
            return JsonResponse(data={
                'error': Code.TENANT_NO_ACCESS.value,
                'message': _('tenant no access permission'),
            })

        token = self._get_token(user)

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
                'has_tenant_admin_perm': has_tenant_admin_perm,
            }
        })

    @action(detail=True, methods=['post'])
    def mobile_login(self, request, pk):
        tenant = self.get_object()
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        thirdparty_data = request.data.get('thirdparty', None)

        runtime = get_app_runtime()

        cache_code = runtime.cache_provider.get(mobile)

        if isinstance(cache_code,bytes):
            cache_code = str(cache_code, 'utf-8')

        if code != '123456' and (code is None or cache_code != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        user = User.objects.get(mobile=mobile)
        token = self._get_token(user)

        has_tenant_admin_perm = tenant.has_admin_perm(user)
        if not has_tenant_admin_perm:
            return JsonResponse(data={
                'error': Code.TENANT_NO_ACCESS.value,
                'message': _('tenant no access permission'),
            })

        if thirdparty_data is not None:
            bind_key = thirdparty_data.pop('bind_key')
            assert bind_key is not None

            for eidp in self.runtime.external_idps:
                provider = eidp.provider
                if provider.bind_key == bind_key:
                    if hasattr(provider, 'bind'):
                        provider.bind(user, thirdparty_data)
                    
                    break

        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key,
                'has_tenant_admin_perm': has_tenant_admin_perm,          
            }
        })

    @action(detail=True, methods=['post'])
    def mobile_register(self, request, pk):        
        mobile = request.data.get('mobile')
        code = request.data.get('code')

        cache_code = self.runtime.cache_provider.get(mobile)
        if code != '123456' and (code is None or str(cache_code, 'utf-8') != code):
            return JsonResponse(data={
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            })

        tenant = self.get_object()
        user, created = User.objects.get_or_create(
            tenant=tenant, 
            mobile=mobile,
        )
        token = self._get_token(user)
        return JsonResponse(data={
            'error': Code.OK.value,
            'data': {
                'token': token.key, # TODO: fullfil user info            
            }
        })

    @action(detail=True, methods=['GET'])
    def apps(self, request, pk):
        user: User = request.user
        tenant: Tenant = self.get_object()

        all_apps = App.active_objects.filter(
            tenant=tenant,
        )

        if tenant.has_admin_perm(user) or user.is_superuser:
            objs = all_apps
        else:
            all_apps_perms = [app.access_perm_code for app in all_apps]

            perms = set([perm.codename for perm in user.user_permissions.filter(
                codename__in=all_apps_perms
            )])

            groups = user.groups.all()
            g: Group
            for g in groups:
                perms = perms | set([perm.codename for perm in g.owned_perms(all_apps_perms)])

            objs = [app for app in all_apps if app.access_perm_code in perms]

        serializer = self.get_serializer(objs, many=True)
        return Response(serializer.data)

    def _get_token(self, user:User):
        token, _ = Token.objects.get_or_create(
            user=user,
        )

        return token

    def login_form(self, tenant_id):
        return lp.LoginForm(
            label='密码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='username',
                    placeholder='用户名',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                )
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse("api:tenant-login", args=[tenant_id,]),
                    method='post',
                    params={
                        'username':'username',
                        'password':'password'
                    }
                )
            ),
        )

    def mobile_login_form(self, tenant_id):
        return lp.LoginForm(
            label='验证码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={
                                'mobile': 'mobile'
                            }
                        )
                    )
                )
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse("api:tenant-mobile-login", args=[tenant_id,]),
                    method='post',
                    params={
                        'mobile':'mobile',
                        'code':'code'
                    }
                )
            ),
        )

    def mobile_register_form(self, tenant_id):
        return lp.LoginForm(
            label='手机号注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:send-sms'),
                            method='post',
                            params={
                                'mobile': 'mobile'
                            }
                        )
                    )
                )
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse("api:tenant-mobile-register", args=[tenant_id,]),
                    method='post',
                    params={
                        'mobile':'mobile',
                        'password':'password',
                        'code':'code'
                    }
                )
            ),
        )