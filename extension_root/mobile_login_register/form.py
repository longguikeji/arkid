#!/usr/bin/env python3

from common.loginpage import BaseForm, FormItem, Button, ButtonHttp
from django.urls import reverse


class MobileLoginForm(BaseForm):
    form_label = '验证码登录'
    form_items = [
        FormItem('mobile', 'text', '手机号'),
        FormItem('code', 'text', '验证码'),
    ]

    def set_form_item_button(self, login_form_item):
        if login_form_item['name'] == 'mobile':
            payload = {
                'auth_code_length': self.provider.auth_code_length or 6,
            }
            login_form_item['append'] = Button(
                label='发送验证码',
                delay=60,
                http=ButtonHttp(
                    url=reverse('api:sms', args=['login']),
                    method='post',
                    params={'mobile': 'mobile'},
                    payload=payload,
                ),
            )


class MobileRegisterForm(BaseForm):
    form_label = '手机号注册'

    form_items = [
        FormItem('mobile', 'text', '手机号'),
        FormItem('code', 'text', '验证码'),
        FormItem('password', 'password', '密码'),
        FormItem('checkpassword', 'password', '密码确认'),
    ]

    def set_form_item_button(self, login_form_item):
        if login_form_item['name'] == 'mobile':
            payload = {
                'auth_code_length': self.provider.auth_code_length or 6,
            }
            login_form_item['append'] = Button(
                label='发送验证码',
                delay=60,
                http=ButtonHttp(
                    url=reverse('api:sms', args=['register']),
                    method='post',
                    params={'mobile': 'mobile'},
                    payload=payload,
                ),
            )


class MobileResetPWDForm(BaseForm):
    form_label = '通过手机号修改密码'

    form_items = [
        FormItem('mobile', 'text', '手机号'),
        FormItem('code', 'text', '验证码'),
        FormItem('password', 'password', '新密码'),
        FormItem('checkpassword', 'password', '新密码确认'),
    ]

    def set_form_item_button(self, login_form_item):
        if login_form_item['name'] == 'mobile':
            payload = {
                'auth_code_length': self.provider.auth_code_length or 6,
            }
            login_form_item['append'] = Button(
                label='发送验证码',
                delay=60,
                http=ButtonHttp(
                    url=reverse('api:sms', args=['reset_password']),
                    method='post',
                    params={'mobile': 'mobile'},
                    payload=payload,
                ),
            )
