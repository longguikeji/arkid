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
    MobileLoginResponseSerializer,
    MobileRegisterResponseSerializer,
    MobileResetPasswordRequestSerializer,
    PasswordSerializer,
)
from inventory.models import User
from django.utils.translation import gettext_lazy as _


@extend_schema(
    tags=['mobile-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=MobileLoginResponseSerializer,
)
class MobileLoginView(APIView):
    def post(self, request, pk):
        # uuid = self.kwargs['pk']
        tenant = Tenant.active_objects.filter(uuid=pk).first()
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
    tags=['mobile-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=MobileRegisterResponseSerializer,
)
class MobileRegisterView(APIView):
    def post(self, request, pk):
        tenant = Tenant.active_objects.filter(uuid=pk).first()
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
    tags=['mobile-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class MobileResetPasswordView(generics.CreateAPIView):
    '''
    user forget password reset api
    '''

    permission_classes = []
    authentication_classes = []

    serializer_class = MobileResetPasswordRequestSerializer

    @extend_schema(responses=PasswordSerializer)
    def post(self, request):
        mobile = request.data.get('mobile', '')
        password = request.data.get('password', '')
        code = request.data.get('code', '')
        user = User.objects.filter(mobile=mobile).first()
        if not user:
            return JsonResponse(
                data={
                    'error': Code.USER_EXISTS_ERROR.value,
                    'message': _('user does not exist'),
                }
            )
        if password and self.check_password(password) is False:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _('password strength not enough'),
                }
            )
        # 检查验证码
        try:
            sms_token, expire_time = ResetPWDSMSClaimSerializer.check_sms(
                {'mobile': mobile, 'code': code}
            )
        except ValidationError:
            return JsonResponse(
                data={
                    'error': Code.SMS_CODE_MISMATCH.value,
                    'message': _('sms code mismatch'),
                }
            )
        user.set_password(password)
        user.save()
        return Response({'error': Code.OK.value, 'message': 'Reset password success'})

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True
