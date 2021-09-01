#!/usr/bin/env python3

from common.loginpage import BaseForm, FormItem, Button, ButtonHttp
from django.urls import reverse


class EmailRegisterForm(BaseForm):
    form_label = '邮箱注册'

    form_items = [
        FormItem('email', 'text', '邮箱账号'),
        FormItem('code', 'text', '验证码'),
        FormItem('password', 'password', '密码'),
        FormItem('checkpassword', 'password', '密码确认'),
    ]

    def set_form_item_button(self, login_form_item):
        if login_form_item['name'] == 'email':
            login_form_item['append'] = Button(
                label='发送验证码',
                delay=60,
                http=ButtonHttp(
                    url=reverse('api:email', args=['register'])
                    + '?send_verify_code=true',
                    method='post',
                    params={'email': 'email'},
                ),
            )


class EmailResetPWDForm(BaseForm):
    form_label = '通过邮箱修改密码'

    form_items = [
        FormItem('email', 'text', '邮箱账号'),
        FormItem('code', 'text', '验证码'),
        FormItem('password', 'password', '新密码'),
        FormItem('checkpassword', 'password', '新密码确认'),
    ]

    def set_form_item_button(self, login_form_item):
        if login_form_item['name'] == 'email':
            login_form_item['append'] = Button(
                label='发送验证码',
                delay=60,
                http=ButtonHttp(
                    url=reverse('api:email', args=['reset_password'])
                    + '?send_verify_code=true',
                    method='post',
                    params={'email': 'email'},
                ),
            )
