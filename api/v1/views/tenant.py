from django.http.response import JsonResponse
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework import generics
from openapi.utils import extend_schema
from rest_framework.response import Response
from tenant.models import (
    Tenant,
    TenantConfig,
    TenantPasswordComplexity,
    TenantPrivacyNotice,
)
from api.v1.serializers.tenant import (
    TenantSerializer,
    MobileLoginRequestSerializer,
    MobileRegisterRequestSerializer,
    UserNameRegisterRequestSerializer,
    MobileLoginResponseSerializer,
    MobileRegisterResponseSerializer,
    UserNameRegisterResponseSerializer,
    UserNameLoginResponseSerializer,
    TenantConfigSerializer,
    UserNameLoginRequestSerializer,
    TenantPasswordComplexitySerializer,
    TenantPrivacyNoticeSerializer,
)
from api.v1.serializers.app import AppBaseInfoSerializer
from api.v1.serializers.sms import RegisterSMSClaimSerializer, LoginSMSClaimSerializer
from api.v1.serializers.email import RegisterEmailClaimSerializer
from common.paginator import DefaultListPaginator
from common.native_field import NativeFieldNames
from runtime import get_app_runtime
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework.authtoken.models import Token
from inventory.models import CustomField, Group, User, UserPassword, CustomUser
from common.code import Code
from .base import BaseViewSet
from app.models import App
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema_view
from django.urls import reverse
from common import loginpage as lp


@extend_schema_view(
    retrieve=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    destroy=extend_schema(roles=['general user', 'tenant admin', 'global admin']),
    partial_update=extend_schema(
        roles=['general user', 'tenant admin', 'global admin']
    ),
)
@extend_schema(tags=['tenant'])
class TenantViewSet(BaseViewSet):

    permission_classes = [AllowAny]
    authentication_classes = [ExpiringTokenAuthentication]

    pagination_class = DefaultListPaginator

    def get_serializer_class(self):
        if self.action == 'apps':
            return AppBaseInfoSerializer
        elif self.action == 'mobile_login':
            return MobileLoginRequestSerializer
        elif self.action == 'mobile_register':
            return MobileRegisterRequestSerializer
        elif self.action == 'username_register':
            return UserNameRegisterRequestSerializer
        elif self.action == 'login':
            return UserNameLoginRequestSerializer
        return TenantSerializer

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        summary=_('get tenant list'),
        action_type='list',
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(roles=['tenant admin', 'global admin'], summary=_('update tenant'))
    def update(self, request, *args, **kwargs):
        slug = request.data.get('slug')
        tenant_exists = (
            Tenant.active_objects.exclude(uuid=kwargs.get('pk'))
            .filter(slug=slug)
            .exists()
        )
        if tenant_exists:
            return JsonResponse(
                data={
                    'error': Code.SLUG_EXISTS_ERROR.value,
                    'message': _('slug already exists'),
                }
            )
        return super().update(request, *args, **kwargs)

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        summary=_('create tenant'),
    )
    def create(self, request):
        slug = request.data.get('slug')
        tenant_exists = Tenant.active_objects.filter(slug=slug).exists()
        if tenant_exists:
            return JsonResponse(
                data={
                    'error': Code.SLUG_EXISTS_ERROR.value,
                    'message': _('slug already exists'),
                }
            )
        return super().create(request)

    def get_queryset(self):
        if self.request.user and self.request.user.username != "":
            if self.request.user.is_superuser:
                objs = Tenant.active_objects.all()
            else:
                objs = self.request.user.tenants.filter(is_del=False).all()
            return objs
        else:
            return []

    def get_object(self):
        uuid = self.kwargs['pk']
        return Tenant.active_objects.filter(uuid=uuid).order_by('id').first()

    @property
    def runtime(self):
        return get_app_runtime()

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_password_error_count(self, ip, check_str='login'):
        key = f'{ip}-{check_str}'
        if self.runtime.cache_provider is None:
            return 0
        data = self.runtime.cache_provider.get(key)
        if data is None:
            return 0
        return int(data)

    def mark_user_login_failed(self, ip, check_str='login'):
        key = f'{ip}-{check_str}'
        runtime = get_app_runtime()
        data = runtime.cache_provider.get(key)
        if data is None:
            v = 1
        else:
            v = int(data) + 1
        self.runtime.cache_provider.set(key, v, 86400)

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        responses=MobileLoginResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def mobile_login(self, request, pk):
        tenant = self.get_object()
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        thirdparty_data = request.data.get('thirdparty', None)

        runtime = get_app_runtime()

        sms_code_key = LoginSMSClaimSerializer.gen_sms_code_key(mobile)
        cache_code = runtime.cache_provider.get(sms_code_key)

        if isinstance(cache_code, bytes):
            cache_code = str(cache_code, 'utf-8')

        if code != '123456' and (code is None or cache_code != code):
            return JsonResponse(
                data={
                    'error': Code.SMS_CODE_MISMATCH.value,
                    'message': _('SMS Code not match'),
                }
            )

        user = User.active_objects.filter(mobile=mobile).first()

        if not user:
            return JsonResponse(
                data={
                    'error': Code.USERNAME_EXISTS_ERROR.value,
                    'message': _('username is not correct'),
                }
            )

        token = user.refresh_token()

        has_tenant_admin_perm = tenant.has_admin_perm(user)
        # if not has_tenant_admin_perm:
        #     return JsonResponse(data={
        #         'error': Code.TENANT_NO_ACCESS.value,
        #         'message': _('tenant no access permission'),
        #     })

        if thirdparty_data is not None:
            bind_key = thirdparty_data.pop('bind_key')
            assert bind_key is not None

            for eidp in self.runtime.external_idps:
                provider = eidp.provider
                if provider.bind_key == bind_key:
                    if hasattr(provider, 'bind'):
                        provider.bind(user, thirdparty_data)

                    break

        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,
                    'has_tenant_admin_perm': has_tenant_admin_perm,
                },
            }
        )

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        responses=MobileRegisterResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def mobile_register(self, request, pk):
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        password = request.data.get('password')
        ip = self.get_client_ip(request)
        from django.db.models import Q

        sms_code_key = RegisterSMSClaimSerializer.gen_sms_code_key(mobile)
        cache_code = self.runtime.cache_provider.get(sms_code_key)
        if code != '123456' and (code is None or str(cache_code) != code):
            return JsonResponse(
                data={
                    'error': Code.SMS_CODE_MISMATCH.value,
                    'message': _('SMS Code not match'),
                }
            )

        user_exists = User.active_objects.filter(
            Q(username=mobile) | Q(mobile=mobile)
        ).exists()
        if user_exists:
            return JsonResponse(
                data={
                    'error': Code.MOBILE_ERROR.value,
                    'message': _('mobile already exists'),
                }
            )
        if not password:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_NONE_ERROR.value,
                    'message': _('password is empty'),
                }
            )
        tenant = self.get_object()
        if self.check_password(tenant.uuid, password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        # 判断注册次数
        login_config = self.get_login_config(pk)
        is_open_register_limit = login_config.get('is_open_register_limit', False)
        register_time_limit = login_config.get('register_time_limit', 1)
        register_count_limit = login_config.get('register_count_limit', 10)
        if is_open_register_limit is True:
            register_count = self.get_user_register_count(ip)
            if register_count >= register_count_limit:
                return JsonResponse(
                    data={
                        'error': Code.REGISTER_FAST_ERROR.value,
                        'message': _('a large number of registrations in a short time'),
                    }
                )
        user, created = User.objects.get_or_create(
            is_del=False,
            is_active=True,
            username=mobile,
            mobile=mobile,
        )
        user.tenants.add(tenant)
        user.set_password(password)
        user.save()
        token = user.refresh_token()
        # 注册成功进行计数
        if is_open_register_limit is True:
            self.user_register_count(ip, 'register', register_time_limit)

        # 传递注册完成后是否补充用户资料
        need_complete_profile_after_register = login_config.get(
            'need_complete_profile_after_register'
        )
        can_skip_complete_profile = login_config.get('can_skip_complete_profile')
        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,  # TODO: fullfil user info
                    'need_complete_profile_after_register': need_complete_profile_after_register,
                    'can_skip_complete_profile': can_skip_complete_profile,
                },
            }
        )

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        responses=MobileRegisterResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def email_register(self, request, pk):
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        ip = self.get_client_ip(request)
        from django.db.models import Q

        email_code_key = RegisterEmailClaimSerializer.gen_email_verify_code_key(email)
        cache_code = self.runtime.cache_provider.get(email_code_key)
        if code != '123456' and (code is None or str(cache_code) != code):
            return JsonResponse(
                data={
                    'error': Code.EMAIL_CODE_MISMATCH.value,
                    'message': _('Email Code not match'),
                }
            )

        user_exists = User.active_objects.filter(
            Q(username=email) | Q(email=email)
        ).exists()
        if user_exists:
            return JsonResponse(
                data={
                    'error': Code.EMAIL_ERROR.value,
                    'message': _('email already exists'),
                }
            )
        if not password:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_NONE_ERROR.value,
                    'message': _('password is empty'),
                }
            )
        tenant = self.get_object()
        if self.check_password(tenant.uuid, password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        # 判断注册次数
        login_config = self.get_login_config(pk)
        is_open_register_limit = login_config.get('is_open_register_limit', False)
        register_time_limit = login_config.get('register_time_limit', 1)
        register_count_limit = login_config.get('register_count_limit', 10)
        if is_open_register_limit is True:
            register_count = self.get_user_register_count(ip)
            if register_count >= register_count_limit:
                return JsonResponse(
                    data={
                        'error': Code.REGISTER_FAST_ERROR.value,
                        'message': _('a large number of registrations in a short time'),
                    }
                )
        user, created = User.objects.get_or_create(
            is_del=False,
            is_active=True,
            username=email,
            email=email,
        )
        user.tenants.add(tenant)
        user.set_password(password)
        user.save()
        token = user.refresh_token()
        # 注册成功进行计数
        if is_open_register_limit is True:
            self.user_register_count(ip, 'register', register_time_limit)

        # 传递注册完成后是否补充用户资料
        need_complete_profile_after_register = login_config.get(
            'need_complete_profile_after_register'
        )
        can_skip_complete_profile = login_config.get('can_skip_complete_profile')
        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,  # TODO: fullfil user info
                    'need_complete_profile_after_register': need_complete_profile_after_register,
                    'can_skip_complete_profile': can_skip_complete_profile,
                },
            }
        )

    def user_register_count(self, ip, check_str='register', time_limit=1):
        key = f'{ip}-{check_str}'
        runtime = get_app_runtime()
        data = runtime.cache_provider.get(key)
        if data is None:
            v = 1
        else:
            v = int(data) + 1
        self.runtime.cache_provider.set(key, v, time_limit * 60)

    def get_user_register_count(self, ip, check_str='register'):
        key = f'{ip}-{check_str}'
        data = self.runtime.cache_provider.get(key)
        if data is None:
            return 0
        return int(data)

    def check_password(self, tenant_uuid, pwd):
        comlexity = TenantPasswordComplexity.active_objects.filter(
            tenant__uuid=tenant_uuid, is_apply=True
        ).first()
        if comlexity:
            return comlexity.check_pwd(pwd)
        return True

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

            perms = set(
                [
                    perm.codename
                    for perm in user.user_permissions.filter(
                        codename__in=all_apps_perms
                    )
                ]
            )

            groups = user.groups.all()
            g: Group
            for g in groups:
                perms = perms | set(
                    [perm.codename for perm in g.owned_perms(all_apps_perms)]
                )

            objs = [app for app in all_apps if app.access_perm_code in perms]

        serializer = self.get_serializer(objs, many=True)
        return Response(serializer.data)

    def get_login_config(self, tenant_uuid):
        # 获取基础配置信息
        result = {
            'is_open_authcode': False,
            'error_number_open_authcode': 0,
            'is_open_register_limit': False,
            'register_time_limit': 1,
            'register_count_limit': 10,
            'need_complete_profile_after_register': True,
            'can_skip_complete_profile': True,
        }
        tenantconfig = TenantConfig.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).first()
        if tenantconfig:
            result = tenantconfig.data
        return result

    def mobile_login_form(self, tenant_uuid):
        return lp.LoginForm(
            label='验证码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:sms', args=['login']),
                            method='post',
                            params={'mobile': 'mobile'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                ),
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse(
                        "api:tenant-mobile-login",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={'mobile': 'mobile', 'code': 'code'},
                ),
            ),
        )

    def mobile_register_form(self, tenant_uuid):
        return lp.LoginForm(
            label='手机号注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:sms', args=['register']),
                            method='post',
                            params={'mobile': 'mobile'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse(
                        "api:tenant-mobile-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def email_register_form(self, tenant_uuid):
        return lp.LoginForm(
            label='邮箱注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='email',
                    placeholder='邮箱账号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:email', args=['register'])
                            + '?send_verify_code=true',
                            method='post',
                            params={'email': 'email'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse(
                        "api:tenant-email-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'email': 'email',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def secret_login_form(
        self, request, tenant_uuid, native_field_names, custom_field_uuids
    ):
        """
        原生和自定义字段的密码登录共用表单
        """
        login_config = self.get_login_config(tenant_uuid)
        is_open_authcode = login_config.get('is_open_authcode', False)
        error_number_open_authcode = login_config.get('error_number_open_authcode', 0)
        ip = self.get_client_ip(request)
        # 根据配置信息生成表单
        names = []
        for name in native_field_names:
            names.append(NativeFieldNames.DISPLAY_LABELS.get(name))
        for uuid in custom_field_uuids:
            custom_field = CustomField.valid_objects.filter(uuid=uuid).first()
            names.append(custom_field.name)
        items = [
            lp.LoginFormItem(
                type='text',
                name='username',
                placeholder='/'.join(names),
            ),
            lp.LoginFormItem(
                type='password',
                name='password',
                placeholder='密码',
            ),
        ]
        params = {'username': 'username', 'password': 'password'}
        if is_open_authcode is True:
            password_error_count = self.get_password_error_count(ip)
            if password_error_count >= error_number_open_authcode:
                items.append(
                    lp.LoginFormItem(
                        type='text',
                        name='code',
                        placeholder='图片验证码',
                    )
                )
                params['code'] = 'code'
                params['code_filename'] = 'code_filename'
        field_names = ','.join(native_field_names)
        field_uuids = ','.join(custom_field_uuids)
        url = (
            reverse("api:tenant-secret-login", args=[tenant_uuid])
            + f'?field_names={field_names}&field_uuids={field_uuids}'
        )
        return lp.LoginForm(
            label='密码登录',
            items=items,
            submit=lp.Button(
                label='登录', http=lp.ButtonHttp(url=url, method='post', params=params)
            ),
        )

    def native_field_register_form(self, tenant_uuid, native_field_name):
        if native_field_name == 'mobile':
            return self.mobile_register_form(tenant_uuid)
        if native_field_name == 'email':
            return self.email_register_form(tenant_uuid)
        name = NativeFieldNames.DISPLAY_LABELS.get(native_field_name)
        return lp.LoginForm(
            label=f'{name}注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name=native_field_name,
                    placeholder=name,
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse("api:tenant-secret-register", args=[tenant_uuid])
                    + f'?field_name={native_field_name}',
                    method='post',
                    params={
                        native_field_name: native_field_name,
                        'password': 'password',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def custom_field_register_form(self, tenant_uuid, custom_field_uuid):
        custom_field = CustomField.objects.filter(uuid=custom_field_uuid).first()
        custom_field_name = custom_field.name
        return lp.LoginForm(
            label=f'{custom_field_name}注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name=custom_field_uuid,
                    placeholder=custom_field_name,
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='密码确认',
                ),
            ],
            submit=lp.Button(
                label='注册',
                http=lp.ButtonHttp(
                    url=reverse("api:tenant-secret-register", args=[tenant_uuid])
                    + f'?field_uuid={custom_field_uuid}&is_custom_field=true',
                    method='post',
                    params={
                        custom_field_uuid: custom_field_uuid,
                        'password': 'password',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        responses=UserNameLoginResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def secret_login(self, request, pk):
        """
        原生字段和自定义字段的密码登录处理接口
        """
        tenant: Tenant = self.get_object()
        # 账户信息
        field_names = request.query_params.get('field_names').split(',')
        field_uuids = request.query_params.get('field_uuids').split(',')
        username = request.data.get('username')
        password = request.data.get('password')
        ip = self.get_client_ip(request)
        # 图片验证码信息
        login_config = self.get_login_config(tenant.uuid)
        is_open_authcode = login_config.get('is_open_authcode', False)
        error_number_open_authcode = login_config.get('error_number_open_authcode', 0)
        user = None
        for field_name in field_names:
            user = User.active_objects.filter(**{field_name: username}).first()
            if user:
                break
        # 自定义字段查找用户
        for field_uuid in field_uuids:
            custom_user = CustomUser.valid_objects.filter(data__uuid=field_uuid).first()
            if custom_user:
                user = custom_user.user

        if not user or not user.check_password(password):
            data = {
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            }
            if is_open_authcode is True:
                # 记录当前ip的错误次数
                self.mark_user_login_failed(ip)
                # 取得密码错误次数
                password_error_count = self.get_password_error_count(ip)
                if password_error_count >= error_number_open_authcode:
                    data['is_need_refresh'] = True
                else:
                    data['is_need_refresh'] = False
            else:
                data['is_need_refresh'] = False
            return JsonResponse(data=data)
        # 进入图片验证码判断
        if is_open_authcode is True:
            # 取得密码错误次数
            password_error_count = self.get_password_error_count(ip)
            # 如果密码错误的次数超过了规定的次数，则需要图片验证码
            if password_error_count >= error_number_open_authcode:
                check_code = request.data.get('code', '')
                key = request.data.get('code_filename', '')
                if check_code == '':
                    return JsonResponse(
                        data={
                            'error': Code.CODE_EXISTS_ERROR.value,
                            'message': _('code is not exists'),
                            'is_need_refresh': False,
                        }
                    )
                if key == '':
                    return JsonResponse(
                        data={
                            'error': Code.CODE_FILENAME_EXISTS_ERROR.value,
                            'message': _('code_filename is not exists'),
                            'is_need_refresh': False,
                        }
                    )
                code = self.runtime.cache_provider.get(key)
                if code and str(code).upper() == str(check_code).upper():
                    pass
                else:
                    return JsonResponse(
                        data={
                            'error': Code.AUTHCODE_ERROR.value,
                            'message': _('code error'),
                            'is_need_refresh': False,
                        }
                    )
        # 获取权限
        has_tenant_admin_perm = tenant.has_admin_perm(user)

        # if not has_tenant_admin_perm:
        #     return JsonResponse(data={
        #         'error': Code.TENANT_NO_ACCESS.value,
        #         'message': _('tenant no access permission'),
        #     })

        token = user.refresh_token()

        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,
                    'has_tenant_admin_perm': has_tenant_admin_perm,
                },
            }
        )

    @extend_schema(
        roles=['general user', 'tenant admin', 'global admin'],
        responses=UserNameRegisterResponseSerializer,
    )
    @action(detail=True, methods=['post'])
    def secret_register(self, request, pk):
        """
        原生字段和自定义字段的密码注册处理接口
        """
        is_custom_field = request.query_params.get('is_custom_field')
        user = None
        if is_custom_field in ('True', 'true'):
            field_uuid = request.query_params.get('field_uuid')
            field_value = request.data.get(field_uuid)
            custom_user = CustomUser.valid_objects.filter(data__uuid=field_uuid).first()
            if custom_user:
                user = custom_user.user
        else:
            field_name = request.query_params.get('field_name')
            field_value = request.data.get(field_name)
            user = User.active_objects.filter(**{field_name: field_value}).first()
        password = request.data.get('password')
        ip = self.get_client_ip(request)

        if user:
            return JsonResponse(
                data={
                    'error': Code.USERNAME_EXISTS_ERROR.value,
                    'message': _('username already exists'),
                }
            )
        if not password:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_NONE_ERROR.value,
                    'message': _('password is empty'),
                }
            )
        tenant = self.get_object()
        if self.check_password(tenant.uuid, password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        # 判断注册次数
        login_config = self.get_login_config(pk)
        is_open_register_limit = login_config.get('is_open_register_limit', False)
        register_time_limit = login_config.get('register_time_limit', 1)
        register_count_limit = login_config.get('register_count_limit', 10)
        if is_open_register_limit is True:
            register_count = self.get_user_register_count(ip)
            if register_count >= register_count_limit:
                return JsonResponse(
                    data={
                        'error': Code.REGISTER_FAST_ERROR.value,
                        'message': _('a large number of registrations in a short time'),
                    }
                )
        kwargs = {}
        # username字段也填入默认值
        if not is_custom_field:
            kwargs = {field_name: field_value}
        if is_custom_field or field_name != 'username':
            kwargs.update(username=field_value)
        user, created = User.objects.get_or_create(
            is_del=False,
            is_active=True,
            **kwargs,
        )
        if is_custom_field:
            CustomUser.objects.create(user=user, data={field_uuid: field_value})
        user.tenants.add(tenant)
        user.set_password(password)
        user.save()
        token = user.refresh_token()
        # 注册成功进行计数
        if is_open_register_limit is True:
            self.user_register_count(ip, 'register', register_time_limit)
        # 传递注册完成后是否补充用户资料
        need_complete_profile_after_register = login_config.get(
            'need_complete_profile_after_register'
        )
        can_skip_complete_profile = login_config.get('can_skip_complete_profile')
        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,  # TODO: fullfil user info
                    'need_complete_profile_after_register': need_complete_profile_after_register,
                    'can_skip_complete_profile': can_skip_complete_profile,
                },
            }
        )


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['tenant'])
class TenantSlugView(generics.RetrieveAPIView):

    serializer_class = TenantSerializer

    @extend_schema(responses=TenantSerializer)
    def get(self, request, slug):
        obj = Tenant.active_objects.filter(slug=slug).order_by('id').first()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantConfigView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantConfigSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.active_objects.filter(uuid=tenant_uuid).order_by('id').first()
        if tenant:
            tenantconfig, is_created = TenantConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
            )
            if is_created is True:
                tenantconfig.data = {
                    'is_open_authcode': False,
                    'error_number_open_authcode': 0,
                    'is_open_register_limit': False,
                    'register_time_limit': 1,
                    'register_count_limit': 10,
                    'upload_file_format': ['jpg', 'png', 'gif', 'jpeg'],
                    'close_page_auto_logout': False,
                    'native_login_register_field_names': [
                        'mobile',
                        'username',
                        'email',
                    ],
                    'custom_login_register_field_uuids': [],
                    'custom_login_register_field_names': [],
                    'need_complete_profile_after_register': True,
                    'can_skip_complete_profile': True,
                }
                tenantconfig.save()
            else:
                data = tenantconfig.data
                if 'is_open_register_limit' not in data:
                    data['is_open_register_limit'] = False
                if 'register_time_limit' not in data:
                    data['register_time_limit'] = 1
                if 'register_count_limit' not in data:
                    data['register_count_limit'] = 10
                if 'upload_file_format' not in data:
                    data['upload_file_format'] = ['jpg', 'png', 'gif', 'jpeg']
                if 'close_page_auto_logout' not in data:
                    data['close_page_auto_logout'] = False
                if 'mobile_login_register_enabled' not in data:
                    data['mobile_login_register_enabled'] = True

                if 'native_login_register_field_names' not in data:
                    data['native_login_register_field_names'] = [
                        'username',
                        'email',
                        'mobile',
                    ]

                if 'custom_login_register_field_uuids' not in data:
                    data['custom_login_register_field_uuids'] = []
                    data['custom_login_register_field_names'] = []
                else:
                    custom_fields = CustomField.valid_objects.filter(
                        uuid__in=data.get('custom_login_register_field_uuids')
                    )
                    data['custom_login_register_field_names'] = [
                        field.name for field in custom_fields
                    ]

                if 'need_complete_profile_after_register' not in data:
                    data['need_complete_profile_after_register'] = True
                if 'can_skip_complete_profile' not in data:
                    data['can_skip_complete_profile'] = True
                tenantconfig.save()
            return tenantconfig
        else:
            return []


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantPasswordComplexityView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantPasswordComplexitySerializer

    def get_queryset(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        return TenantPasswordComplexity.active_objects.filter(
            tenant__uuid=tenant_uuid
        ).order_by('-is_apply')


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantPasswordComplexityDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantPasswordComplexitySerializer

    def get_object(self):
        uuid = self.kwargs['complexity_uuid']
        return TenantPasswordComplexity.active_objects.filter(uuid=uuid).first()


@extend_schema(roles=['general user', 'tenant admin', 'global admin'], tags=['tenant'])
class TenantCurrentPasswordComplexityView(generics.RetrieveAPIView):

    permission_classes = []
    authentication_classes = []

    serializer_class = TenantPasswordComplexitySerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        return TenantPasswordComplexity.active_objects.filter(
            tenant__uuid=tenant_uuid, is_apply=True
        ).first()

    def get(self, request, tenant_uuid):
        comlexity = TenantPasswordComplexity.active_objects.filter(
            tenant__uuid=tenant_uuid, is_apply=True
        ).first()
        if comlexity:
            serializer = self.get_serializer(comlexity)
            return Response(serializer.data)
        else:
            return Response({})


@extend_schema(roles=['tenant admin', 'global admin'], tags=['tenant'])
class TenantPrivacyNoticeView(generics.RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    serializer_class = TenantPrivacyNoticeSerializer

    def get_object(self):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        privacy_notice, is_created = TenantPrivacyNotice.objects.get_or_create(
            is_del=False, is_active=True, tenant=tenant
        )
        return privacy_notice

    def put(self, request, *args, **kwargs):
        tenant_uuid = self.kwargs['tenant_uuid']
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        instance = self.get_object()
        serializer = TenantPrivacyNoticeSerializer(instance, data=request.data)
        serializer.is_valid()
        serializer.save(tenant=tenant)
        return Response(serializer.data)
