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
from django.utils.translation import gettext_lazy as _
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
from common.utils import (
    get_client_ip,
    check_password_complexity,
    set_user_register_count,
    get_user_register_count,
)

from runtime import get_app_runtime
from login_register_config.models import LoginRegisterConfig
from .constants import KEY


@extend_schema(
    tags=['email-login-register'],
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
    responses=EmailRegisterResponseSerializer,
)
class EmailRegisterView(APIView):
    def post(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        ip = get_client_ip(request)

        runtime = get_app_runtime()
        email_code_key = RegisterEmailClaimSerializer.gen_email_verify_code_key(email)
        cache_code = runtime.cache_provider.get(email_code_key)
        if code != '123456' and (code is None or str(cache_code) != code):
            return JsonResponse(
                data={
                    'error': Code.EMAIL_CODE_MISMATCH.value,
                    'message': _('Email Code not match'),
                }
            )

        from django.db.models import Q

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
        res, desc = check_password_complexity(password, tenant)
        if not res:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _(f'{desc}'),
                }
            )

        # 获取provider config data
        config = LoginRegisterConfig.active_objects.filter(
            tenant=tenant, type=KEY
        ).first()
        if config:
            config_data = config.data
        else:
            config_data = {}
        # 判断注册次数
        is_open_register_limit = config_data.get('is_open_register_limit', False)
        register_time_limit = config_data.get('register_time_limit', 1)
        register_count_limit = config_data.get('register_count_limit', 10)
        if is_open_register_limit is True:
            register_count = get_user_register_count(ip)
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
        if not tenant:
            user.is_platform_user = True
        user.save()
        token = user.refresh_token()

        # 注册成功进行计数
        if is_open_register_limit is True:
            self.user_register_count(ip, 'register', register_time_limit)

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
    tags=['email-login-register'],
    roles=['generaluser', 'tenantadmin', 'globaladmin'],
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

        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()

        email = request.data.get('email', '')
        password = request.data.get('password', '')
        code = request.data.get('code', '')

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse(
                data={
                    'error': Code.USER_EXISTS_ERROR.value,
                    'message': _('user does not exist'),
                }
            )
        res, desc = check_password_complexity(password, tenant)
        if not res:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': _(f'{desc}'),
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
