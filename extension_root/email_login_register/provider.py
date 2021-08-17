from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config


class EmailLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self) -> None:
        super().__init__()

    def register_form(self, tenant_uuid):
        return lp.LoginForm(
            label='邮箱注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='email',
                    placeholder='邮箱账号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:email', args=['register'])
                            + '?send_verify_code=true',
                            method='post',
                            params={'email': 'email'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
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
                    url=reverse(
                        "api:tenant-email-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'email': 'email',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def reset_password_form(self):
        return lp.LoginForm(
            label='通过邮箱修改密码',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='email',
                    placeholder='邮箱账号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:email', args=['reset_password'])
                            + '?send_verify_code=true',
                            method='post',
                            params={'email': 'email'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='password',
                    placeholder='新密码',
                ),
                lp.LoginFormItem(
                    type='password',
                    name='checkpassword',
                    placeholder='新密码确认',
                ),
            ],
            submit=lp.Button(
                label='确认',
                http=lp.ButtonHttp(
                    url=reverse(
                        "api:user-email-reset-password",
                    ),
                    method='post',
                    params={
                        'email': 'email',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
                gopage=lp.LOGIN,
            ),
        )
