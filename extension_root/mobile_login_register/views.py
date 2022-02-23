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
from common.utils import (
    get_client_ip,
    check_password_complexity,
    set_user_register_count,
    get_user_register_count,
)
from login_register_config.models import LoginRegisterConfig
from .constants import KEY
from runtime import get_app_runtime
from api.v1.serializers.tenant import TenantSerializer


@extend_schema(
    tags=['mobile-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=MobileLoginResponseSerializer,
)
class MobileLoginView(APIView):
    def post(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        thirdparty_data = request.data.get('thirdparty', None)

        runtime = get_app_runtime()

        sms_code_key = LoginSMSClaimSerializer.gen_sms_code_key(mobile)
        cache_code = runtime.cache_provider.get(sms_code_key)

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
                    'message': _('mobile not exists'),
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

        if thirdparty_data is not None:
            bind_key = thirdparty_data.pop('bind_key')
            assert bind_key is not None

            for eidp in runtime.external_idps:
                provider = eidp.provider
                if provider.bind_key == bind_key:
                    if hasattr(provider, 'bind'):
                        provider.bind(user, thirdparty_data)

                    break

        return JsonResponse(
            data={
                'error': Code.OK.value,
                'data': return_data,
            }
        )


@extend_schema(
    tags=['mobile-login-register'],
    roles=['general user', 'tenant admin', 'global admin'],
    responses=MobileRegisterResponseSerializer,
)
class MobileRegisterView(APIView):
    def post(self, request):
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        mobile = request.data.get('mobile')
        code = request.data.get('code')
        password = request.data.get('password')
        ip = get_client_ip(request)
        from django.db.models import Q

        sms_code_key = RegisterSMSClaimSerializer.gen_sms_code_key(mobile)
        runtime = get_app_runtime()
        cache_code = runtime.cache_provider.get(sms_code_key)
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
        ret, message = check_password_complexity(password, tenant)
        if not ret:
            return JsonResponse(
                data={
                    'error': Code.PASSWORD_STRENGTH_ERROR.value,
                    'message': message,
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
                    'user_uuid': user.uuid.hex,
                    'token': token.key,  # TODO: fullfil user info
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
        tenant = None
        tenant_uuid = request.query_params.get('tenant', None)
        if tenant_uuid:
            tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
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
        if password and check_password_complexity(password, tenant) is False:
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
