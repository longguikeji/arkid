from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config


class MobileLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self) -> None:
        super().__init__()

    def login_form(self, tenant_uuid):
        return lp.LoginForm(
            label='验证码登录',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:sms', args=['login']),
                            method='post',
                            params={'mobile': 'mobile'},
                        ),
                    ),
                ),
                lp.LoginFormItem(
                    type='text',
                    name='code',
                    placeholder='验证码',
                ),
            ],
            submit=lp.Button(
                label='登录',
                http=lp.ButtonHttp(
                    url=reverse(
                        "api:mobile_login_register:mobile-login",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={'mobile': 'mobile', 'code': 'code'},
                ),
            ),
        )

    def register_form(self, tenant_uuid):
        return lp.LoginForm(
            label='手机号注册',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:sms', args=['register']),
                            method='post',
                            params={'mobile': 'mobile'},
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
                        "api:mobile_login_register:mobile-register",
                        args=[
                            tenant_uuid,
                        ],
                    ),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
            ),
        )

    def reset_password_form(self):
        return lp.LoginForm(
            label='通过手机号修改密码',
            items=[
                lp.LoginFormItem(
                    type='text',
                    name='mobile',
                    placeholder='手机号',
                    append=lp.Button(
                        label='发送验证码',
                        delay=60,
                        http=lp.ButtonHttp(
                            url=reverse('api:sms', args=['reset_password']),
                            method='post',
                            params={'mobile': 'mobile'},
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
                        "api:mobile_login_register:mobile-reset-password",
                    ),
                    method='post',
                    params={
                        'mobile': 'mobile',
                        'password': 'password',
                        'code': 'code',
                        'checkpassword': 'checkpassword',
                    },
                ),
                gopage=lp.LOGIN,
            ),
        )
