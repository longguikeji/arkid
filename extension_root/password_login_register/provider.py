from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config
from common.native_field import NativeFieldNames
from inventory.models import CustomField, Group, User, UserPassword, CustomUser
from tenant.models import Tenant


class PasswordLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self) -> None:
        super().__init__()

    def login_form(self, request, tenant_uuid, native_field_names, custom_field_uuids):
        """
        原生和自定义字段的密码登录共用表单
        """
        login_config = self.get_login_config(tenant_uuid)
        is_open_authcode = login_config.get('is_open_authcode', False)
        error_number_open_authcode = login_config.get('error_number_open_authcode', 0)
        ip = self.get_client_ip(request)
        # 根据配置信息生成表单
        names = []
        for name in native_field_names:
            names.append(NativeFieldNames.DISPLAY_LABELS.get(name))
        for uuid in custom_field_uuids:
            custom_field = CustomField.valid_objects.filter(uuid=uuid).first()
            names.append(custom_field.name)
        items = [
            lp.LoginFormItem(
                type='text',
                name='username',
                placeholder='/'.join(names),
            ),
            lp.LoginFormItem(
                type='password',
                name='password',
                placeholder='密码',
            ),
        ]
        params = {'username': 'username', 'password': 'password'}
        if is_open_authcode is True:
            password_error_count = self.get_password_error_count(ip)
            if password_error_count >= error_number_open_authcode:
                items.append(
                    lp.LoginFormItem(
                        type='text',
                        name='code',
                        placeholder='图片验证码',
                    )
                )
                params['code'] = 'code'
                params['code_filename'] = 'code_filename'
        field_names = ','.join(native_field_names)
        field_uuids = ','.join(custom_field_uuids)
        url = (
            reverse("api:tenant-secret-login", args=[tenant_uuid])
            + f'?field_names={field_names}&field_uuids={field_uuids}'
        )
        return lp.LoginForm(
            label='密码登录',
            items=items,
            submit=lp.Button(
                label='登录', http=lp.ButtonHttp(url=url, method='post', params=params)
            ),
        )

    def register_form(self, tenant_uuid, field_name, is_custom_field):
        # TODO 将原生字段的注册表单和自定义字段的注册表单统一起来
        tenant = Tenant.active_objects.filter(uuid=tenant_uuid).first()
        if is_custom_field:
            custom_field = CustomField.objects.filter(
                name=field_name, tenant=tenant
            ).first()
            display_name = custom_field.name
        else:
            display_name = NativeFieldNames.DISPLAY_LABELS.get(field_name)
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
                    url=reverse("api:tenant-secret-register", args=[tenant_uuid])
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
