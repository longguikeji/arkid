from asyncio.log import logger
from distutils import core
import re
from unicodedata import name
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.api import operation
from .error import ErrorCode
from arkid.core.models import Tenant, User
from arkid.core import pages,actions
from arkid.extension.models import TenantExtensionConfig
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
from django.db.models import Q
from arkid.core.extension import create_extension_schema_by_package
from .schema import *
from api.v1.pages.user_manage.user_list import page as user_list_page
from api.v1.schema.auth import AuthIn
from arkid.core.constants import TENANT_ADMIN, PLATFORM_ADMIN

package = "com.longgui.auth.factor.password"
select_pw_login_fields_page = pages.TablePage(select=True, name=_("Select Password Login Fields", "选择密码登录字段"))


PasswordAuthFactorSchema = create_extension_schema_by_package('PasswordAuthFactorSchema',package, 
        [
            ('reset_password_enabled', Optional[bool] , Field(deprecated=True)),
            ('login_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('login_enabled_field_names', '启用密码登录的字段'),
                    page=select_pw_login_fields_page.tag,
                    link="key",
                    type="string",
                )
            ),
            ('register_enabled_field_names', List[str],
                Field(
                    default=[], 
                    title=_('register_enabled_field_names', '启用密码注册的字段'),
                    page=select_pw_login_fields_page.tag,
                    link="key",
                    type="string",
                )
            ),
            ('is_apply', bool , Field(default=False, title=_('is_apply', '是否启用密码校验'))),
            ('regular', str, Field(default='', title=_('regular', '密码校验正则表达式'))),
            ('title', str, Field(default='', title=_('title', '密码校验提示信息'))),
        ],
        BaseAuthFactorSchema,
    )

RestUserPasswordIn = create_extension_schema_by_package('RestUserPasswordIn',package, 
        [
            ('password', str , Field(title='新密码',type='password')),
       ],
    )

GetUserKeyFieldItemOut = create_extension_schema_by_package('GetUserKeyFieldItemOut',package, 
        [
            ('key', str , Field()),
            ('name', str,Field()),
       ],
    )

class PasswordAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_extend_field(UserPassword, "password")
        self.register_auth_factor_schema(PasswordAuthFactorSchema, 'password')
        self.register_extend_api(AuthIn, password=str)
        user_key_fields_path = self.register_api(
            '/user_key_fields/',
            'GET',
            self.get_user_key_fields,
            response=List[GetUserKeyFieldItemOut],
        )
        select_pw_login_fields_page.create_actions(
            init_action=actions.DirectAction(
                path=user_key_fields_path,
                method=actions.FrontActionMethod.GET,
            ),
        )
        self.register_front_pages(select_pw_login_fields_page)
        
        # 租户管理员：用户管理-用户列表-重置密码
        reset_user_password_path = self.register_api(
            '/reset_user_password/{id}/',
            'POST',
            self.reset_user_password,
            tenant_path=True,
            response=ResponseSchema,
        )
        
        user_list_page.add_local_actions(
            actions.OpenAction(
                name='重置密码',
                path=reset_user_password_path,
                method=actions.FrontActionMethod.POST,
            )
        )
        
        # 初始化部分配置数据
        tenant = Tenant.platform_tenant()
        if not self.get_tenant_configs(tenant):
            config = {
                'login_enabled_field_names': ['username'],
                'register_enabled_field_names': ['username'],
                'is_apply': False,
                'regular': '',
                'title': '',
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
    
    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def reset_user_password(self, request, tenant_id:str, id:str, data:RestUserPasswordIn):
        user = User.active_objects.get(id=id)
        password = data.password
        user.password = make_password(password)
        user.save()
        return self.success()
        
    def get_user_key_fields(self,request):
        data = [{'key':key,'name':value} for key,value in User.key_fields.items()]
        return data
    
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        config_id = request.POST.get('config_id')
        config = TenantExtensionConfig.active_objects.get(id=config_id).config
        login_enabled_field_names = config.get('login_enabled_field_names')
        filter_params = None
        for lefn in login_enabled_field_names:
            temp = {lefn:username}
            if filter_params:
                filter_params = Q(**temp) | filter_params
            else:
                filter_params = Q(**temp)
        users = User.expand_objects.filter(tenant=tenant).filter(filter_params)
        if len(users) > 1:
            logger.error(f'{username}在{login_enabled_field_names}中匹配到多个用户')
            return self.auth_failed(event, data=self.error(ErrorCode.CONTACT_MANAGER))
        user = users[0]
        if user:
            user_password = user.get("password")
            if user_password:
                if check_password(password, user_password):
                    user = User.active_objects.get(id=user.get("id"))
                    return self.auth_success(user, event)
        
        return self.auth_failed(event, data=self.error(ErrorCode.USERNAME_PASSWORD_MISMATCH))

    @transaction.atomic()
    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        password = request.POST.get('password')

        config = self.get_current_config(event)
        ret, message = self.check_password_complexity(password, config)
        if not ret:
            return self.error(ErrorCode.PASSWORD_STRENGTH_LACK)
        
        register_fields = config.config.get('register_enabled_field_names')
        if not register_fields:
            fields = ['username']
            if request.POST.get('username') is None:
                self.auth_failed(event, data=self.error(ErrorCode.USERNAME_EMPTY))
        else:
            fields = [k for k in register_fields if request.POST.get(k) is not None]
            if not fields:
                self.auth_failed(event, data=self.error(ErrorCode.ALL_USER_FLAG_LACK_FIELD))

        for field in fields:
            user = self._get_register_user(tenant, field, request.POST.get(field))
            if user:
                self.auth_failed(event, data=self.error(ErrorCode.FIELD_USER_EXISTS, field=field))

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
        username_placeholder = ""
        for lefn in config.config.get('login_enabled_field_names',[]):
            if username_placeholder:
                username_placeholder = ',' + User.key_fields[lefn]
            else:
                username_placeholder = User.key_fields[lefn]
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": username_placeholder
            },
            {
                "type": "password",
                "name": "password",
                "placeholder": "密码"
            },
        ]
        self.add_page_form(config, self.LOGIN, "密码登录", items)

    def create_register_page(self, event, config):
        items = []
        register_fields = config.config.get('register_enabled_field_names')
        for rf in register_fields:
            items.append({
                "type": "text",
                "name": rf,
                "placeholder": User.key_fields[rf]
            })
        items.extend([
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
        ])
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
        
        mine_password_path = self.register_api(
            "/mine_password/",
            'POST',
            self.update_mine_password,
            tenant_path=True,
            response=UpdateMinePasswordOut,
        )
        
        name = '更改密码'

        page = pages.FormPage(name=name)
        page.create_actions(
            init_action=actions.ConfirmAction(
                path=mine_password_path,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=mine_password_path
                ),
            }
        )
        return page
    
    def update_mine_password(self,request, tenant_id: str,data:UpdateMinePasswordIn):
        """更改密码"""
        user = request.user
        user = UserPassword.objects.filter(target=user).first()
        user_password = user.password
        if not user_password or check_password(data.old_password, user_password):
            if data.password == data.confirm_password:
                user.password = make_password(data.password)
                user.save()
                return self.success()
            else:
                return self.error(ErrorCode.TWO_TIME_PASSWORD_MISMATCH)
        
        return self.error(ErrorCode.OLD_PASSWORD_ERROR)


extension = PasswordAuthFactorExtension(
    package=package,
    name="密码认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='wely@longguikeji.com',
)