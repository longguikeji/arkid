import os
import requests
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from urllib.parse import urlencode, unquote
import urllib.parse
from django.urls import reverse
from config import get_app_config
from tenant.models import Tenant
from openapi.utils import extend_schema
from rest_framework import generics
from runtime import get_app_runtime
from api.v1.serializers.sms import (
    RegisterSMSClaimSerializer,
    LoginSMSClaimSerializer,
    ResetPWDSMSClaimSerializer,
)
from django.http.response import JsonResponse
from common.code import Code
from .serializers import (
    PasswordRegisterResponseSerializer,
    PasswordLoginResponseSerializer,
)
from inventory.models import User
from api.v1.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
)
from django.utils.translation import gettext_lazy as _
from inventory.models import CustomField, Group, User, UserPassword, CustomUser
from login_register_config.models import LoginRegisterConfig
from .constants import KEY
from common.utils import (
    get_client_ip,
    check_password_complexity,
    set_user_register_count,
    get_user_register_count,
    get_password_error_count,
)
from api.v1.serializers.tenant import TenantSerializer


@extend_schema(
    tags=['password-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=PasswordLoginResponseSerializer,
)
class PasswordLoginView(APIView):
    def post(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        # 获取登录注册配置
        config = LoginRegisterConfig.valid_objects.filter(
            tenant=tenant, type=KEY
        ).first()
        if not config:
            username_login_enabled = True
            email_login_enabled = True
            login_enabled_custom_field_names = []
        else:
            username_login_enabled = config.data.get('username_login_enabled', True)
            email_login_enabled = config.data.get('email_login_enabled', False)
            login_enabled_custom_field_names = config.data.get(
                'login_enabled_custom_field_names', None
            )

        username = request.data.get('username')
        password = request.data.get('password')
        ip = get_client_ip(request)

        # 图片验证码信息
        is_open_authcode = config.data.get('is_open_authcode', False)
        error_number_open_authcode = config.data.get('error_number_open_authcode', 0)
        user = None
        if username_login_enabled:
            user = User.active_objects.filter(username=username).first()
        if not user and email_login_enabled:
            user = User.active_objects.filter(email=username).first()
        if not user and login_enabled_custom_field_names:

            # 自定义字段查找用户
            for name in login_enabled_custom_field_names:
                custom_field = CustomField.valid_objects.filter(
                    name=name, subject='user'
                )
                assert custom_field is not None
                if not custom_field:
                    continue
                custom_user = CustomUser.valid_objects.filter(data__name=name).first()
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
                password_error_count = get_password_error_count(ip)
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
            password_error_count = get_password_error_count(ip)
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
        # 如果是子账户，要自动转为主账户
        if user.parent:
            user = user.parent

        token = user.refresh_token()

        return_data = {'token': token.key, 'user_uuid': user.uuid.hex}
        if tenant:
            return_data['has_tenant_admin_perm'] = tenant.has_admin_perm(user)
        else:
            return_data['tenants'] = [
                TenantSerializer(o).data for o in user.tenants.all()
            ]

        return JsonResponse(data={'error': Code.OK.value, 'data': return_data})


@extend_schema(
    tags=['email-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=PasswordRegisterResponseSerializer,
)
class PasswordRegisterView(APIView):
    def post(self, request):
        """
        原生字段和自定义字段的密码注册处理接口
        """
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        is_custom_field = request.query_params.get('is_custom_field', None)
        user = None
        if is_custom_field in ('True', 'true'):
            field_name = request.query_params.get('field_name')
            custom_field = CustomField.valid_objects.filter(
                name=field_name, subject='user'
            )
            assert custom_field is not None
            field_value = request.data.get(field_name)

            custom_user = CustomUser.valid_objects.filter(data__name=field_name).first()
            if custom_user:
                user = custom_user.user
        else:
            field_name = request.query_params.get('field_name')
            field_value = request.data.get(field_name)
            user = User.active_objects.filter(**{field_name: field_value}).first()

        password = request.data.get('password')
        ip = get_client_ip(request)

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
        if check_password_complexity(password, tenant) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )

        # 获取登录注册配置
        config = LoginRegisterConfig.valid_objects.filter(
            tenant=tenant, type=KEY
        ).first()
        if not config:
            is_open_register_limit = False
            register_time_limit = 1
            register_count_limit = 10
        else:
            is_open_register_limit = config.data.get('is_open_register_limit', False)
            register_time_limit = config.data.get('register_time_limit', 1)
            register_count_limit = config.data.get('register_count_limit', 10)
        if is_open_register_limit is True:
            register_count = get_user_register_count(ip)
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
            if field_name != 'username':
                kwargs.update(username=field_value)
            user, created = User.objects.get_or_create(
                is_del=False,
                is_active=True,
                **kwargs,
            )
        else:
            user = User.objects.create(
                is_del=False,
                is_active=True,
                username=field_value,
            )
            CustomUser.objects.create(user=user, data={field_name: field_value})
        user.tenants.add(tenant)
        user.set_password(password)

        if not tenant:
            user.is_platform_user = True

        user.save()
        token = user.refresh_token()
        # 注册成功进行计数
        if is_open_register_limit is True:
            set_user_register_count(ip, 'register', register_time_limit)
        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': {
                    'token': token.key,  # TODO: fullfil user info
                    'user_uuid': user.uuid.hex,
                },
            }
        )


@extend_schema(
    tags=['password-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class LoginFieldsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request):
        data = []
        data.append({'value': 'username', 'label': '用户名'})
        data.append({'value': 'email', 'label': '邮箱账号'})
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        custom_fields = CustomField.valid_objects.filter(subject='user', tenant=tenant)
        for field in custom_fields:
            data.append({'value': field.name, 'label': field.name})

        return JsonResponse(data=data, safe=False)


@extend_schema(
    tags=['password-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class RegisterFieldsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request):
        data = []
        data.append({'value': 'username', 'label': '用户名'})
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        custom_fields = CustomField.valid_objects.filter(subject='user', tenant=tenant)
        for field in custom_fields:
            data.append({'value': field.name, 'label': field.name})

        return JsonResponse(data=data, safe=False)
