from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config
from common.native_field import NativeFieldNames
from inventory.models import CustomField, Group, User, UserPassword, CustomUser
from tenant.models import Tenant
from common.utils import (
    get_client_ip,
    check_password_complexity,
    set_user_register_count,
    get_user_register_count,
    get_password_error_count,
)
from rest_framework.exceptions import ValidationError

from .form import PasswordLoginForm, PasswordRegisterForm
from common.exception import ValidationFailed
from common.code import Code
from django.utils.translation import gettext_lazy as _


class PasswordLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data=None, request=None, tenant=None) -> None:
        self.username_login_enabled = data.get('username_login_enabled', True)
        self.username_register_enabled = data.get('username_register_enabled', True)
        self.email_login_enabled = data.get('email_login_enabled', False)
        self.login_enabled_custom_field_names = data.get(
            'login_enabled_custom_field_names', []
        )
        self.register_enabled_custom_field_names = data.get(
            'register_enabled_custom_field_names', []
        )
        # self.is_open_authcode = data.get('is_open_authcode', False)
        # self.error_number_open_authcode = data.get('error_number_open_authcode', 0)
        self.request = request
        self.tenant = tenant

    @property
    def login_form(self):
        return PasswordLoginForm(self).get_form()

    @property
    def register_form(self):
        forms = []
        if self.username_register_enabled:
            forms.append(PasswordRegisterForm(self, 'username', '用户名').get_form())
        for name in self.register_enabled_custom_field_names:
            forms.append(PasswordRegisterForm(self, name, name).get_form())
        return forms

    def authenticate(self, request):
        ''' '''

        username = request.data.get('username')
        password = request.data.get('password')
        user = self._get_login_user(username)
        if not user or not user.check_password(password):
            data = {
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            }

            return data
        else:
            data = {
                'error': Code.OK.value,
                'user': user,
            }
            return data

    def register_user(self, request):
        # TODO password verify
        if 'username' in request.data:
            field_name = 'username'
        elif 'email' in request.data:
            field_name = 'email'
        else:
            for key in request.data:
                if key not in ('password', 'checkpassword'):
                    field_name = key
                    break

        field_value = request.data.get(field_name)
        user = self._get_register_user(field_name, field_value)
        if user:
            data = {
                'error': Code.USERNAME_EXISTS_ERROR.value,
                'message': _('username already exists'),
            }
            return data
        # username字段也填入默认值
        if field_name in ('username', 'email'):
            kwargs = {field_name: field_value}
            if field_name == 'email':
                kwargs.update(username=field_value)
            user = User.objects.create(
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

        data = {'error': Code.OK.value, 'user': user}
        return data

    def _get_login_user(self, username):
        user = None
        if self.username_login_enabled:
            user = User.active_objects.filter(username=username).first()
        if not user and self.email_login_enabled:
            user = User.active_objects.filter(email=username).first()
        if not user and self.login_enabled_custom_field_names:

            # 自定义字段查找用户
            for name in self.login_enabled_custom_field_names:
                custom_field = CustomField.valid_objects.filter(
                    name=name, subject='user'
                )
                if not custom_field:
                    continue
                custom_user = CustomUser.valid_objects.filter(data__name=name).first()
                if custom_user:
                    user = custom_user.user
        return user

    def _get_register_user(self, field_name, field_value):
        user = None
        if field_name in ('username', 'email'):
            user = User.active_objects.filter(**{field_name: field_value}).first()
        else:
            custom_field = CustomField.valid_objects.filter(
                name=field_name, subject='user'
            )
            if not custom_field:
                return None

            custom_user = CustomUser.valid_objects.filter(data__name=field_name).first()
            if custom_user:
                user = custom_user.user
        return user

    # def login_form(self, tenant_uuid=None, **kwargs):
    #     """
    #     原生和自定义字段的密码登录共用表单
    #     """
    #     request = kwargs.get('request')
    #     ip = get_client_ip(request)

    #     account_names = []
    #     if self.username_login_enabled:
    #         account_names.append(NativeFieldNames.DISPLAY_LABELS.get('username'))
    #     if self.email_login_enabled:
    #         account_names.append(NativeFieldNames.DISPLAY_LABELS.get('email'))

    #     account_names.extend(self.login_enabled_custom_field_names)
    #     if not account_names:
    #         return None

    #     items = [
    #         lp.LoginFormItem(
    #             type='text',
    #             name='username',
    #             placeholder='/'.join(account_names),
    #         ),
    #         lp.LoginFormItem(
    #             type='password',
    #             name='password',
    #             placeholder='密码',
    #         ),
    #     ]
    #     params = {'username': 'username', 'password': 'password'}
    #     if self.is_open_authcode is True:
    #         password_error_count = get_password_error_count(ip)
    #         if password_error_count >= self.error_number_open_authcode:
    #             items.append(
    #                 lp.LoginFormItem(
    #                     type='text',
    #                     name='code',
    #                     placeholder='图片验证码',
    #                 )
    #             )
    #             params['code'] = 'code'
    #             params['code_filename'] = 'code_filename'
    #     submit_url = reverse("api:password_login_register:password-login")
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'
    #     return lp.LoginForm(
    #         label='密码登录',
    #         items=items,
    #         submit=lp.Button(
    #             label='登录',
    #             http=lp.ButtonHttp(url=submit_url, method='post', params=params),
    #         ),
    #     )

    # def register_form(self, tenant_uuid=None, **kwargs):
    #     result = []
    #     if self.username_login_enabled:
    #         display_name = NativeFieldNames.DISPLAY_LABELS.get('username')
    #         result.append(
    #             self._register_form(tenant_uuid, 'username', display_name, False)
    #         )

    #     for custom_field in self.register_enabled_custom_field_names:
    #         result.append(
    #             self._register_form(tenant_uuid, custom_field, custom_field, True)
    #         )
    #     return result

    # def _register_form(self, tenant_uuid, field_name, display_name, is_custom_field):
    #     submit_url = (
    #         reverse("api:password_login_register:password-register")
    #         + f'?field_name={field_name}&is_custom_field={is_custom_field}'
    #     )
    #     if tenant_uuid:
    #         submit_url = submit_url + f'?tenant={tenant_uuid}'
    #     return lp.LoginForm(
    #         label=f'{display_name}注册',
    #         items=[
    #             lp.LoginFormItem(
    #                 type='text',
    #                 name=field_name,
    #                 placeholder=display_name,
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
    #                 url=reverse("api:password_login_register:password-register")
    #                 + f'?field_name={field_name}&is_custom_field={is_custom_field}',
    #                 method='post',
    #                 params={
    #                     field_name: field_name,
    #                     'password': 'password',
    #                     'checkpassword': 'checkpassword',
    #                 },
    #             ),
    #         ),
    #     )
