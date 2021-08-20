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


@extend_schema(
    tags=['password-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=PasswordLoginResponseSerializer,
)
class PasswordLoginView(APIView):
    def post(self, request, pk):
        # uuid = self.kwargs['pk']
        tenant = Tenant.active_objects.filter(uuid=pk).first()
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
    tags=['email-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=PasswordRegisterResponseSerializer,
)
class PasswordRegisterView(APIView):
    def post(self, request, pk):
        """
        原生字段和自定义字段的密码注册处理接口
        """
        tenant = Tenant.active_objects.filter(uuid=pk).first()

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
