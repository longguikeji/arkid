
from asyncio.log import logger
import json
import re
from typing_extensions import Self

from django.conf import settings
from arkid.config import get_app_config
from arkid.core.api import GlobalAuth, operation
from arkid.core.error import ErrorDict, SuccessDict
from arkid.core.event import Event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.models import User,UserGroup
from arkid.core.token import refresh_token
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.constants import *
from arkid.core import pages,actions, routers
from arkid.core.translation import gettext_default as _
from .ldap import LdapAuth
from .schema import *
from .error import ErrorCode


class LDAPAuthFactorExtension(AuthFactorExtension):
    
    def load(self):
        super().load()
        self.register_extension_api()
        self.register_extension_config_schema()
    
    def register_extension_api(self):
        """注册插件所需API
        """
        self.user_fields_path = self.register_api(
            '/user_fields/',
            'GET',
            self.user_fields,
            tenant_path=False,
            auth=GlobalAuth(),
            response=UserFieldsOut,
        )
    
    def register_extension_config_schema(self):
        """注册认证因素配置
        """
        UserAttributeMapping = create_extension_schema(
            "UserAttributeMapping",
            __file__,
            fields=[
                (
                    "key",
                    str,
                    Field(
                        path=self.user_fields_path,
                        method="get",
                        format="autocomplete",
                        title=_("字段名")
                    )
                ),
                (
                    "value",
                    str,
                    Field(
                        title=_("映射名")
                    )
                )
            ]
        )

        LdapAuthFactorSchema = create_extension_schema(
            'LdapAuthFactorSchema',
            __file__, 
            [
                (
                    'reset_password_enabled',
                    Optional[bool] , 
                    Field(deprecated=True)
                ),
                (
                    'host', 
                    str,
                    Field(
                        title=_("Host")
                    )
                ),
                (
                    'port', 
                    int,
                    Field(
                        title=_("Port"),
                        default=389
                    )
                ),
                (
                    'bind_dn',
                    str , 
                    Field(
                        title=_('bind_dn', '登录名')
                    )
                ),
                (
                    'bind_password',
                    str , 
                    Field(
                        title=_('bind_password', '登录密码')
                    )
                ),
                (
                    "user_search_base",
                    str,
                    Field(
                        title=_('User Search Base'),
                        default="ou=user,dc=example,dc=org"
                    )
                ),
                (
                    "user_object_class",
                    str,
                    Field(
                        title=_('User Object Class'),
                        default="inetOrgPerson"
                    )
                ),
                (
                    "username_attr",
                    str,
                    Field(
                        title=_('User Attributes'),
                        default="cn"
                    )
                ),
                (
                    "user_attr_map",
                    List[UserAttributeMapping],
                    Field(
                        title=_("用户信息字段映射"),
                        format='dynamic',
                        type="array",
                        default=[
                            {
                                "key":"usernmae",
                                "value":"cn"  
                            },
                        ]
                    )
                ),
                (
                    "use_tls",
                    bool,
                    Field(
                        default=False
                    )
                )
            ],
            BaseAuthFactorSchema,
        )
        self.register_auth_factor_schema(
            LdapAuthFactorSchema,
            "ldap"
        )
    
    @operation(UserFieldsOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_fields(self,request):
        """用户模型字段列表

        Args:
            request (Request): 请求

        Returns:
            list[str]: 字段列表
        """
        data = ["id"]
        data.extend([key for key,value in User.key_fields.items()])
        return self.success(data)
    
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        
        data = request.POST or json.load(request.body)
        
        username = data.get('username')
        password = data.get('password')
        config_id = data.get('config_id')
        
        config = TenantExtensionConfig.active_objects.get(id=config_id).config
        
        user, err_msg = self._get_login_user(tenant, config, username, password)
        
        if not user:
            logger.error(err_msg)
            return self.auth_failed(
                event,
                data = self.error(
                    ErrorCode.AUTHORIZATION_FAILED
                )
            )
        
        return self.auth_success(user,event)
    
    def _get_login_user(self, tenant, config, username, password):
        """访问LDAP server获取登录用户

        Args:
            tenant (Tenant): 租户
            config (dict): 配置
            username (str): 用户名
            password (str): 密码

        Returns:
            tuple(User,str): 用户，错误信息
        """
        settings = {
            "host": config.get("host"),
            "port": config.get("port"),
            "bind_dn": config.get("bind_dn"),
            "bind_password": config.get("bind_password"),
            "user_search_base": config.get("user_search_base"),
            "user_object_class": config.get("user_object_class"),
            "username_attr": config.get("username_attr"),
            "use_tls": config.get("use_tls"),
        }
        auth = LdapAuth(**settings)
        ladp_user_attrs, err_msg = auth.authenticate(username=username, password=password)
        if not ladp_user_attrs:
            return self.error(err_msg)

        user_attrs = {}
        for k, v in self.get_attr_map(config).items():
            if k in ["id"]:
                continue
            
            if v in ladp_user_attrs:
                user_attrs[k] = ladp_user_attrs[v][0] if isinstance(ladp_user_attrs[v],list) else ladp_user_attrs[v]

        # Update or create the user.
        user, created = User.objects.update_or_create(tenant=tenant, **user_attrs)
        return user, None
    
    def get_attr_map(self,config):
        """从配置中组装属性字典

        Args:
            config (dict): 配置

        Returns:
            dict: 属性字典
        """
        user_attr_map = config.get("user_attr_map")
        attr_map = {"username":"cn"}
        if isinstance(user_attr_map,list):
            for item in user_attr_map:
                attr_map[item["key"]] = item["value"]
        
        return attr_map
    def check_auth_data(self, event, **kwargs):
        return super().check_auth_data(event, **kwargs)
    
    def create_auth_manage_page(self):
        _pages = []
        
        update_user_password_path = self.register_api(
            "/update_user_password/",
            'POST',
            self.update_user_password,
            tenant_path=True,
            auth=GlobalAuth(),
            response=UpdateUserPasswordOut
        )
        
        name = 'LDAP代理认证更改密码'

        page = pages.FormPage(name=name)
        page.create_actions(
            init_action=actions.DirectAction(
                path=update_user_password_path,
                method=actions.FrontActionMethod.POST,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=update_user_password_path
                ),
            }
        )
        
        _pages.append(page)
        return _pages
    
    def create_login_page(self, event, config, config_data):
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": "登录名"
            },
            {
                "type": "password",
                "name": "password",
                "placeholder": "密码"
            },
        ]
        self.add_page_form(config, self.LOGIN, config.name, items, config_data)
        
        return super().create_login_page(event, config, config_data)
    
    def create_other_page(self, event, config, config_data):
        return super().create_other_page(event, config, config_data)
    
    def create_password_page(self, event, config, config_data):
        return super().create_password_page(event, config, config_data)
    
    def create_register_page(self, event, config, config_data):
        return super().create_register_page(event, config, config_data)
    
    def fix_login_page(self, event, **kwargs):
        return super().fix_login_page(event, **kwargs)
    
    def register(self, event, **kwargs):
        return super().register(event, **kwargs)
    
    def reset_password(self, event, **kwargs):
        return super().reset_password(event, **kwargs)
    
    @operation(UpdateUserPasswordOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def update_user_password(self,request, tenant_id, data:UpdateUserPasswordIn):
        """更新密码
        """        
        config_instance = self.get_tenant_configs(request.tenant).first()
        
        if not config_instance:
            return self.error(
                ErrorCode.CONFIG_IS_NOT_EXISTS
            )

        if data.password != data.confirm_password:
            return self.error(
                ErrorCode.PASSWORD_NOT_MATCH
            )
            
        config = config_instance.config
        settings = {
            "host": config.get("host"),
            "port": config.get("port"),
            "bind_dn": config.get("bind_dn"),
            "bind_password": config.get("bind_password"),
            "user_search_base": config.get("user_search_base"),
            "user_object_class": config.get("user_object_class"),
            "username_attr": config.get("username_attr"),
            "use_tls": config.get("use_tls"),
        }
        auth = LdapAuth(**settings)
        rs,err = auth.change_password(
            request.user.username,
            data.current_password,
            data.password
        )
        if not rs:
            return self.error(
                err
            )
        return self.success()
    

    
extension = LDAPAuthFactorExtension()
