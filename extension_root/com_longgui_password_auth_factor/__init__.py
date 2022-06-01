from distutils import core
import re
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.error import ErrorCode
from arkid.core.models import Tenant, User
from arkid.core import pages,actions
from .models import UserPassword
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)
from django.db import transaction
from arkid.core.extension import create_extension_schema
from . import views

package = "com.longgui.password_auth_factor"

PasswordAuthFactorSchema = create_extension_schema('PasswordAuthFactorSchema',package, 
        [
            ('reset_password_enabled', Optional[bool] , Field(deprecated=True)),
            ('login_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('login_enabled_field_names', '启用密码登录的字段'),
                    url='/api/v1/login_fields?tenant={tenant_id}'
                )
            ),
            ('register_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('register_enabled_field_names', '启用密码注册的字段'),
                    url='/api/v1/register_fields?tenant={tenant_id}'
                )
            ),
            ('is_apply', bool , Field(default=False, title=_('is_apply', '是否启用密码校验'))),
            ('regular', str, Field(default='', title=_('regular', '密码校验正则表达式'))),
            ('title', str, Field(default='', title=_('title', '密码校验提示信息'))),
        ],
        BaseAuthFactorSchema,
    )

class PasswordAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_extend_field(UserPassword, "password")
        self.register_auth_factor_schema(PasswordAuthFactorSchema, 'password')
        from api.v1.schema.auth import AuthIn
        self.register_extend_api(AuthIn, password=str)
        tenant = Tenant.platform_tenant()
        if not self.get_tenant_configs(tenant):
            config = {
                'reset_password_enabled': True,
                'login_enabled_field_names': ['username'],
                'register_enabled_field_names': ['username'],
                'is_apply': False,
                'regular': '',
                'title': '密码登录',
            }
            self.create_tenant_config(tenant, config, "default", "password")
        try:
            admin_user = User.active_objects.filter(username='admin').first()
            if admin_user:
                admin_password = UserPassword.active_objects.filter(target=admin_user)
                if not admin_password:
                    admin_user.password = make_password('admin')
                    admin_user.save()
        except Exception as e:
            print(e)
        
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.expand_objects.filter(username=username, tenant=tenant).first()
        if user:
            user_password = user.get("password")
            if user_password:
                if check_password(password, user_password):
                    user = User.active_objects.get(id=user.get("id"))
                    return self.auth_success(user, event)
        
        return self.auth_failed(event, data={'error': ErrorCode.USERNAME_PASSWORD_MISMATCH.value, 'message': 'username or password not correct'})

    @transaction.atomic()
    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        password = request.POST.get('password')

        config = self.get_current_config(event)
        ret, message = self.check_password_complexity(password, config)
        if not ret:
            data = {
                'error': ErrorCode.PASSWORD_STRENGTH_ERROR.value,
                'message': message,
            }
            return data
        
        register_fields = config.config.get('register_enabled_field_names')
        if not register_fields:
            fields = ['username']
            if request.POST.get('username') is None:
                self.auth_failed(event, data={'error': ErrorCode.USERNAME_PASSWORD_MISMATCH.value, 'message': 'username不能为空'})
        else:
            fields = [k for k in register_fields if request.POST.get(k) is not None]
            if not fields:
                self.auth_failed(event, data={'error': ErrorCode.USERNAME_PASSWORD_MISMATCH.value, 'message': '所有用户标识至少填一个'})

        for field in fields:
            user = self._get_register_user(tenant, field, request.POST.get(field))
            if user:
                self.auth_failed(event, data={'error': ErrorCode.USERNAME_EXISTS_ERROR.value, 'message': f'{field}字段用户已存在'})

        # user = User.objects.create(tenant=tenant)
        user = User(tenant=tenant)
        for k in fields:
            if request.POST.get(k):
                setattr(user, k, request.POST.get(k))
        user.password = make_password(password)
        user.save()
        tenant.users.add(user)
        tenant.save()

        return user

    def reset_password(self, event, **kwargs):
        pass

    def create_login_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": "用户名"
            },
            {
                "type": "password",
                "name": "password",
                "placeholder": "密码"
            },
        ]
        self.add_page_form(config, self.LOGIN, "密码登录", items)

    def create_register_page(self, event, config):
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": "用户名"
            },
            {
                "type": "password",
                "name": "password",
                "placeholder": "密码"
            },
            {
                "type": "password",
                "name": "checkpassword",
                "placeholder": "密码确认"
            },
        ]
        self.add_page_form(config, self.REGISTER, "用户名密码注册", items)

    def create_password_page(self, event, config):
        pass

    def create_other_page(self, event, config):
        pass
    
    def check_password_complexity(self, pwd, config):
        if not pwd:
            return False, 'No password provide'

        if config:
            regular = config.config.get('regular')
            title = config.config.get('title')
            if re.match(regular, pwd):
                return True, None
            else:
                return False, title
        return True, None

    def _get_register_user(self, tenant, field_name, field_value):
        user = None
        if field_name in ('username', 'email'):
            user = User.active_objects.filter(**{field_name: field_value}).first()
        else:
            # 获取刚注册的用户
            user = User.expand_objects.filter(**{field_name: field_value}).first()
        return user
    
    def create_auth_manage_page(self):
        # 更改密码页面
        
        name = '更改密码'

        page = pages.FormPage(name=name)
        
        pages.register_front_pages(page)

        page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenant/{tenant_id}/mine_password/',
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path="/api/v1/tenant/{tenant_id}/mine_password/"
                ),
            }
        )
        return page


extension = PasswordAuthFactorExtension(
    package=package,
    name="密码认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)