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


class PasswordLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data) -> None:
        self.username_login_enabled = data.get('username_login_enabled', True)
        self.username_register_enabled = data.get('username_register_enabled', True)
        self.email_login_enabled = data.get('email_login_enabled', False)
        self.login_enabled_custom_field_names = data.get(
            'login_enabled_custom_field_names', []
        )
        self.register_enabled_custom_field_names = data.get(
            'register_enabled_custom_field_names', []
        )
        self.is_open_authcode = data.get('is_open_authcode', False)
        self.error_number_open_authcode = data.get('error_number_open_authcode', 0)

    def login_form(self, tenant_uuid=None, **kwargs):
        """
        原生和自定义字段的密码登录共用表单
        """
        request = kwargs.get('request')
        ip = get_client_ip(request)

        account_names = []
        if self.username_login_enabled:
            account_names.append(NativeFieldNames.DISPLAY_LABELS.get('username'))
        if self.email_login_enabled:
            account_names.append(NativeFieldNames.DISPLAY_LABELS.get('email'))

        account_names.extend(self.login_enabled_custom_field_names)
        if not account_names:
            return None

        items = [
            lp.LoginFormItem(
                type='text',
                name='username',
                placeholder='/'.join(account_names),
            ),
            lp.LoginFormItem(
                type='password',
                name='password',
                placeholder='密码',
            ),
        ]
        params = {'username': 'username', 'password': 'password'}
        if self.is_open_authcode is True:
            password_error_count = get_password_error_count(ip)
            if password_error_count >= self.error_number_open_authcode:
                items.append(
                    lp.LoginFormItem(
                        type='text',
                        name='code',
                        placeholder='图片验证码',
                    )
                )
                params['code'] = 'code'
                params['code_filename'] = 'code_filename'
        submit_url = reverse("api:password_login_register:password-login")
        if tenant_uuid:
            submit_url = submit_url + f'?tenant={tenant_uuid}'
        return lp.LoginForm(
            label='密码登录',
            items=items,
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(url=submit_url, method='post', params=params),
            ),
        )

    def register_form(self, tenant_uuid=None, **kwargs):
        result = []
        if self.username_login_enabled:
            display_name = NativeFieldNames.DISPLAY_LABELS.get('username')
            result.append(
                self._register_form(tenant_uuid, 'username', display_name, False)
            )

        for custom_field in self.register_enabled_custom_field_names:
            result.append(
                self._register_form(tenant_uuid, custom_field, custom_field, True)
            )
        return result

    def _register_form(self, tenant_uuid, field_name, display_name, is_custom_field):
        submit_url = (
            reverse("api:password_login_register:password-register")
            + f'?field_name={field_name}&is_custom_field={is_custom_field}'
        )
        if tenant_uuid:
            submit_url = submit_url + f'?tenant={tenant_uuid}'
        return lp.LoginForm(
            label=f'{display_name}注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name=field_name,
                    placeholder=display_name,
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
                    url=reverse("api:password_login_register:password-register")
                    + f'?field_name={field_name}&is_custom_field={is_custom_field}',
                    method='post',
                    params={
                        field_name: field_name,
                        'password': 'password',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def reset_password_form(self, tenant_uuid=None, **kwargs):
        return None
