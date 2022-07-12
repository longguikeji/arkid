
from abc import abstractmethod
from enum import Enum
from ninja import Schema
from pydantic import Field
from arkid.core.extension import Extension
from arkid.core.event import AUTH_SUCCESS, AUTH_FAIL, AUTHFACTOR_CREATE_LOGIN_PAGE, BEFORE_AUTH, CREATE_LOGIN_PAGE_RULES
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from arkid.core.extension import auth_factor


class AuthRuleExtension(Extension):

    TYPE = "auth_rule"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return AuthRuleExtension.TYPE

    def load(self):
        super().load()

        self.listen_events()

    def check_before_auth(self, event, **kwargs):
        if self.check_config(event):
            return self.before_auth(event, **kwargs)

    def check_auth_success(self, event, **kwargs):
        if self.check_config(event):
            return self.auth_success(event, **kwargs)

    def check_auth_fail(self, event, **kwargs):
        if self.check_config(event):
            return self.auth_fail(event, **kwargs)
    
    def check_login_page_rules(self,event, **kwargs):
        return self.login_page_rules(event, **kwargs)
    
    def check_config(self,event)-> bool:
        """检查是否匹配设置

        Args:
            event: 事件

        Returns:
            bool: 匹配结果
        """
        auth_factor_config = event.data["auth_factor_config"]
        config = self.get_current_config(event)
        if config.config.get("main_auth_fator", None):
            if config.config["main_auth_fator"]["id"] == auth_factor_config.id.hex:
                return True
        else:
            return True
        
        return False

    def auth_success(self, event, **kwargs):
        """ 认证成功规则
        """
        pass

    def auth_fail(self, event, **kwargs):
        """ 认证失败规则
        """
        pass

    def before_auth(self, event, auth_factor_config=None, **kwargs):
        """ 认证前规则
        """
        pass
    
    def login_page(self, event,**kwargs):
        """ 登录页面规则
        """
        pass
    
    def login_page_rules(self,event,**kwargs):
        pass

    def register_auth_rule_schema(self, schema, auth_rule_type):
        self.register_config_schema(
            schema, self.package + '_' + auth_rule_type)
        self.register_composite_config_schema(
            schema, auth_rule_type, exclude=['extension'])

    def get_current_config(self, event):
        config_id = event.request.POST.get('config_id')
        return self.get_config_by_id(config_id)

    def listen_events(self):
        
        self.listen_event(BEFORE_AUTH, self.check_before_auth)

        self.listen_event(AUTH_FAIL, self.check_auth_fail)

        self.listen_event(AUTH_SUCCESS, self.check_auth_success)
        
        self.listen_event(CREATE_LOGIN_PAGE_RULES,self.check_login_page_rules)
        
        self.listen_event(AUTHFACTOR_CREATE_LOGIN_PAGE,self.login_page)
class MainAuthRuleSchema(Schema):
    id:str = Field(
        hidden=True,
    )
    
    name:str
    
    package:str = Field(
        hidden=True
    )

class BaseAuthRuleSchema(Schema):
    main_auth_factor: MainAuthRuleSchema = Field(title=_('main_auth_factor', '主认证因素'))
