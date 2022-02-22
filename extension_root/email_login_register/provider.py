from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config
from .form import EmailRegisterForm, EmailResetPWDForm
from api.v1.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
)
from runtime import get_app_runtime
from common.code import Code
from django.utils.translation import gettext_lazy as _
from inventory.models import User
from django.db.models import Q
from common.utils import (
    check_password_complexity,
    get_request_tenant,
)


class EmailLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data=None, request=None, tenant=None) -> None:
        self.register_enabled = data.get('register_enabled', False)
        self.reset_password_enabled = data.get('reset_password_enabled', False)
        self.register_tmpl = data.get('register_tmpl', '')
        self.reset_pwd_tmpl = data.get('reset_pwd_tmpl', '')
        self.auth_code_length = data.get('auth_code_length', '')

    @property
    def register_form(self):
        if self.register_enabled:
            return EmailRegisterForm(self).get_form()
        return None

    @property
    def reset_password_form(self):
        if self.reset_password_enabled:
            return EmailResetPWDForm(self).get_form()
        return None

    def register_user(self, request):

        email = request.data.get('email')
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

        runtime = get_app_runtime()
        email_code_key = RegisterEmailClaimSerializer.gen_email_verify_code_key(email)
        cache_code = runtime.cache_provider.get(email_code_key)
        if not code or cache_code != code:
            data = {
                'error': Code.SMS_CODE_MISMATCH.value,
                'message': _('SMS Code not match'),
            }
            return data

        user_exists = User.objects.filter(Q(username=email) | Q(email=email)).filter(tenants=tenant).exists()
        if user_exists:
            data = {
                'error': Code.EMAIL_ERROR.value,
                'message': _('email already exists'),
            }
            return data

        user = User.objects.create(
            is_del=False,
            is_active=True,
            username=email,
            email=email,
        )

        user.set_password(password)
        user.save()
        data = {'error': Code.OK.value, 'user': user}
        return data

    def reset_password(self, request):

        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')

        runtime = get_app_runtime()
        email_code_key = ResetPWDEmailClaimSerializer.gen_email_verify_code_key(email)
        cache_code = runtime.cache_provider.get(email_code_key)
        if not code or cache_code != code:
            data = {
                'error': Code.EMAIL_CODE_MISMATCH.value,
                'message': _('Email Code not match'),
            }
            return data

        tenant = get_request_tenant(request)
        user = User.objects.filter(email=email, tenants=tenant).first()
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

    # def register_form(self, tenant_uuid=None, **kwargs):
    #     if not self.register_enabled:
    #         return None

    #     submit_url = reverse(
    #         "api:email_login_register:email-register",
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'

    #     return lp.LoginForm(
    #         label='邮箱注册',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='email',
    #                 placeholder='邮箱账号',
    #                 append=lp.Button(
    #                     label='发送验证码',
    #                     delay=60,
    #                     http=lp.ButtonHttp(
    #                         url=reverse('api:email', args=['register'])
    #                         + '?send_verify_code=true',
    #                         method='post',
    #                         params={'email': 'email'},
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
    #                     'email': 'email',
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
    #         "api:email_login_register:email-reset-password",
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'

    #     return lp.LoginForm(
    #         label='通过邮箱修改密码',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name='email',
    #                 placeholder='邮箱账号',
    #                 append=lp.Button(
    #                     label='发送验证码',
    #                     delay=60,
    #                     http=lp.ButtonHttp(
    #                         url=reverse('api:email', args=['reset_password'])
    #                         + '?send_verify_code=true',
    #                         method='post',
    #                         params={'email': 'email'},
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
    #                     'email': 'email',
    #                     'password': 'password',
    #                     'code': 'code',
    #                     'checkpassword': 'checkpassword',
    #                 },
    #             ),
    #             gopage=lp.LOGIN,
    #         ),
    #     )
