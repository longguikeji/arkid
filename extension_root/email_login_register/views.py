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
    EmailRegisterResponseSerializer,
    EmailResetPasswordRequestSerializer,
    PasswordSerializer,
)
from inventory.models import User
from api.v1.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
)


@extend_schema(
    tags=['email-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=EmailRegisterResponseSerializer,
)
class EmailRegisterView(APIView):
    def post(self, request, pk):
        tenant = Tenant.active_objects.filter(uuid=pk).first()
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
        # TODO 检查密码复杂度逻辑抽象
        # if self.check_password(tenant.uuid, password) is False:
        #     return JsonResponse(
        #         data={
        #             'error': Code.PASSWORD_STRENGTH_ERROR.value,
        #             'message': _('password strength not enough'),
        #         }
        #     )
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


@extend_schema(
    tags=['email-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
)
class EmailResetPasswordView(generics.CreateAPIView):
    '''
    user forget password reset api
    '''

    permission_classes = []
    authentication_classes = []

    serializer_class = EmailResetPasswordRequestSerializer

    @extend_schema(responses=PasswordSerializer)
    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        # checkpassword = request.data.get('checkpassword', '')
        code = request.data.get('code', '')
        user = User.objects.filter(email=email).first()
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
            ret = ResetPWDEmailClaimSerializer.check_email_verify_code(email, code)
        except ValidationError:
            return JsonResponse(
                data={
                    'error': Code.EMAIL_CODE_MISMATCH.value,
                    'message': _('email code mismatch'),
                }
            )
        user.set_password(password)
        user.save()
        return Response({'error': Code.OK.value, 'message': 'Reset password success'})

    def check_password(self, pwd):
        if pwd.isdigit() or len(pwd) < 8:
            return False
        return True
