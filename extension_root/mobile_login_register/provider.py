from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config
from .form import MobileLoginForm, MobileRegisterForm, MobileResetPWDForm
from common.code import Code
from runtime import get_app_runtime
from api.v1.serializers.sms import (
    RegisterSMSClaimSerializer,
    LoginSMSClaimSerializer,
    ResetPWDSMSClaimSerializer,
)

from django.utils.translation import gettext_lazy as _
from inventory.models import User
from django.db.models import Q
from common.utils import (
    check_password_complexity,
    get_request_tenant,
)


class MobileLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data=None, request=None, tenant=None) -> None:
        self.login_enabled = data.get('login_enabled', True)
        self.register_enabled = data.get('register_enabled', True)
        self.reset_password_enabled = data.get('reset_password_enabled', True)
        self.auth_code_length = data.get('auth_code_length', '')

    @property
    def login_form(self):
        if self.login_enabled:
            return MobileLoginForm(self).get_form()
        return None

    @property
    def register_form(self):
        if self.register_enabled:
            return MobileRegisterForm(self).get_form()
        return None

    @property
    def reset_password_form(self):
        if self.reset_password_enabled:
            return MobileResetPWDForm(self).get_form()
        return None

    def authenticate(self, request):
        ''' '''

        mobile = request.data.get('mobile')
        code = request.data.get('code')
        runtime = get_app_runtime()

        sms_code_key = LoginSMSClaimSerializer.gen_sms_code_key(mobile)
        cache_code = runtime.cache_provider.get(sms_code_key)

        if not code or cache_code != code:
            data = {
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            }
            return data

        tenant = get_request_tenant(request)
        user = User.active_objects.filter(mobile=mobile,tenants=tenant).first()

        if not user:
            data = {
                'error': Code.USERNAME_EXISTS_ERROR.value,
                'message': _('mobile not exists'),
            }
            return data

        data = {'error': Code.OK.value, 'user': user}
        return data

    def register_user(self, request):

        mobile = request.data.get('mobile')
        code = request.data.get('code')
        password = request.data.get('password')

        tenant = get_request_tenant(request)
        ret, message = check_password_complexity(password, tenant)
        if not ret:
            data = {
                'error': Code.PASSWORD_STRENGTH_ERROR.value,
                'message': message,
            }
            return data

        sms_code_key = RegisterSMSClaimSerializer.gen_sms_code_key(mobile)
        runtime = get_app_runtime()
        cache_code = runtime.cache_provider.get(sms_code_key)
        if not code or cache_code != code:
            data = {
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            }
            return data

        user_exists = User.objects.filter(
            Q(username=mobile) | Q(mobile=mobile)
        ).filter(tenants=tenant).exists()
        if user_exists:
            data = {
                'error': Code.MOBILE_ERROR.value,
                'message': _('mobile already exists'),
            }
            return data

        user = User.objects.create(
            is_del=False,
            is_active=True,
            username=mobile,
            mobile=mobile,
        )
        user.set_password(password)
        user.save()
        data = {'error': Code.OK.value, 'user': user}
        return data

    def reset_password(self, request):

        mobile = request.data.get('mobile')
        code = request.data.get('code')
        password = request.data.get('password')

        sms_code_key = ResetPWDSMSClaimSerializer.gen_sms_code_key(mobile)
        runtime = get_app_runtime()
        cache_code = runtime.cache_provider.get(sms_code_key)
        if not code or cache_code != code:
            data = {
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            }
            return data

        tenant = get_request_tenant(request)
        user = User.objects.filter(mobile=mobile, tenants=tenant).first()
        if not user:
            data = {
                'error': Code.USER_EXISTS_ERROR.value,
                'message': _('user does not exist'),
            }
            return data

        user.set_password(password)
        user.save()
        data = {'error': Code.OK.value, 'user': user}
        return data

    # def login_form(self, tenant_uuid=None, **kwargs):
    #     if not self.login_enabled:
    #         return None

    #     submit_url = reverse(
    #         "api:mobile_login_register:mobile-login",
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'

    #     return lp.LoginForm(
    #         label='验证码登录',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='mobile',
    #                 placeholder='手机号',
    #                 append=lp.Button(
    #                     label='发送验证码',
    #                     delay=60,
    #                     http=lp.ButtonHttp(
    #                         url=reverse('api:sms', args=['login']),
    #                         method='post',
    #                         params={'mobile': 'mobile'},
    #                     ),
    #                 ),
    #             ),
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='code',
    #                 placeholder='验证码',
    #             ),
    #         ],
    #         submit=lp.Button(
    #             label='登录',
    #             http=lp.ButtonHttp(
    #                 url=submit_url,
    #                 method='post',
    #                 params={'mobile': 'mobile', 'code': 'code'},
    #             ),
    #         ),
    #     )

    # def register_form(self, tenant_uuid=None, **kwargs):
    #     if not self.register_enabled:
    #         return None

    #     submit_url = reverse(
    #         "api:mobile_login_register:mobile-register",
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'

    #     return lp.LoginForm(
    #         label='手机号注册',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='mobile',
    #                 placeholder='手机号',
    #                 append=lp.Button(
    #                     label='发送验证码',
    #                     delay=60,
    #                     http=lp.ButtonHttp(
    #                         url=reverse('api:sms', args=['register']),
    #                         method='post',
    #                         params={'mobile': 'mobile'},
    #                     ),
    #                 ),
    #             ),
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='code',
    #                 placeholder='验证码',
    #             ),
    #             lp.LoginFormItem(
    #                 type='password',
    #                 name='password',
    #                 placeholder='密码',
    #             ),
    #             lp.LoginFormItem(
    #                 type='password',
    #                 name='checkpassword',
    #                 placeholder='密码确认',
    #             ),
    #         ],
    #         submit=lp.Button(
    #             label='注册',
    #             http=lp.ButtonHttp(
    #                 url=submit_url,
    #                 method='post',
    #                 params={
    #                     'mobile': 'mobile',
    #                     'password': 'password',
    #                     'code': 'code',
    #                     'checkpassword': 'checkpassword',
    #                 },
    #             ),
    #         ),
    #     )

    # def reset_password_form(self, tenant_uuid=None, **kwargs):
    #     if not self.reset_password_enabled:
    #         return None

    #     submit_url = reverse(
    #         "api:mobile_login_register:mobile-reset-password",
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'

    #     return lp.LoginForm(
    #         label='通过手机号修改密码',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='mobile',
    #                 placeholder='手机号',
    #                 append=lp.Button(
    #                     label='发送验证码',
    #                     delay=60,
    #                     http=lp.ButtonHttp(
    #                         url=reverse('api:sms', args=['reset_password']),
    #                         method='post',
    #                         params={'mobile': 'mobile'},
    #                     ),
    #                 ),
    #             ),
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='code',
    #                 placeholder='验证码',
    #             ),
    #             lp.LoginFormItem(
    #                 type='password',
    #                 name='password',
    #                 placeholder='新密码',
    #             ),
    #             lp.LoginFormItem(
    #                 type='password',
    #                 name='checkpassword',
    #                 placeholder='新密码确认',
    #             ),
    #         ],
    #         submit=lp.Button(
    #             label='确认',
    #             http=lp.ButtonHttp(
    #                 url=submit_url,
    #                 method='post',
    #                 params={
    #                     'mobile': 'mobile',
    #                     'password': 'password',
    #                     'code': 'code',
    #                     'checkpassword': 'checkpassword',
    #                 },
    #             ),
    #             gopage=lp.LOGIN,
    #         ),
    #     )
