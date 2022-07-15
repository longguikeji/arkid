
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
    
    def check_rules(self, event, **kwargs):
        """响应事件: CREATE_LOGIN_PAGE_RULES，遍历所有运行时配置，校验是否通过规则并决定是否进行下一步操作

        Args:
            event (Event): CREATE_LOGIN_PAGE_RULES事件
        """
        for config in self.get_tenant_configs(event.tenant):
            self.check_rule(event, config)
        
    @abstractmethod
    def check_rule(self,event,config):
        """抽象方法：校验规则

        Args:
            event (Event): CREATE_LOGIN_PAGE_RULES事件
            config (TenantExtensionConfig): 运行时配置
        """
        pass

    def register_auth_rule_schema(self, schema, auth_rule_type):
        """注册认证规则运行时schema

        Args:
            schema (Schema): schema描述
            auth_rule_type (str): 认证规则类型
        """
        self.register_config_schema(
            schema, self.package + '_' + auth_rule_type)
        self.register_composite_config_schema(
            schema, auth_rule_type, exclude=['extension'])

    def listen_events(self):
        """监听事件
        """
        self.listen_event(CREATE_LOGIN_PAGE_RULES,self.check_rules)

class MainAuthRuleSchema(Schema):
    """主认证因素描述SCHEMA
    """
    id:str = Field(
        hidden=True,
    )
    
    name:str
    
    package:str = Field(
        hidden=True
    )

class BaseAuthRuleSchema(Schema):
    """认证规则插件基础运行时配置schema
    """
    main_auth_factor: MainAuthRuleSchema = Field(title=_('main_auth_factor', '主认证因素'))
