
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
        # 检查对应的config_id, 如匹配
        
        for config in self.get_tenant_configs(event.tenant):
            self.check_rule(event, config)
        
    @abstractmethod
    def check_rule(self,event,config):
        pass

    def register_auth_rule_schema(self, schema, auth_rule_type):
        self.register_config_schema(
            schema, self.package + '_' + auth_rule_type)
        self.register_composite_config_schema(
            schema, auth_rule_type, exclude=['extension'])

    def listen_events(self):
        self.listen_event(CREATE_LOGIN_PAGE_RULES,self.check_rules)

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
