#!/usr/bin/env python3

from common.loginpage import BaseForm, FormItem, Button, ButtonHttp
from django.urls import reverse


class PasswordLoginForm(BaseForm):
    form_label = '密码登录'
    form_items = [
        FormItem('username', 'text', '用户名'),
        FormItem('password', 'password', '密码'),
    ]

    def set_form_item_placeholder(self, login_form_item):
        if login_form_item['name'] == 'username':
            placeholders = []
            # if self.provider.username_login_enabled:
            #     placeholders.append('用户名')
            # if self.provider.email_login_enabled:
            #     placeholders.append('邮箱账号')
            for name in self.provider.login_enabled_field_names:
                if name == 'username':
                    placeholders.append('用户名')
                elif name == 'email':
                    placeholders.append('邮箱账号')
                else:
                    placeholders.append(name)
            login_form_item['placeholder'] = '/'.join(placeholders)


class PasswordRegisterForm(BaseForm):
    def __init__(self, provider, field_name, field_label):
        super().__init__(provider)
        self.field_name = field_name
        self.field_label = field_label

    def get_form_label(self):
        return f'{self.field_label}注册'

    def get_form_items(self):
        self.form_items = [
            FormItem(self.field_name, 'text', self.field_label),
            FormItem('password', 'password', '密码'),
            FormItem('checkpassword', 'password', '密码确认'),
        ]
        return super().get_form_items()

class UpdatePasswordForm(BaseForm):
    form_label = '修改密码'
    form_items = [
        FormItem('old_password', 'password', '旧密码'),
        FormItem('new_password', 'password', '新密码'),
    ]