
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig

class AuthRuleExtension(Extension):
    
    TYPE = "auth_rule"
    
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig
    
    @property
    def type(self):
        return AuthRuleExtension.TYPE
    
    LOGIN = 'login'
    REGISTER = 'register'
    RESET_PASSWORD = 'password'

    def load(self):
        super().load()

    def register_auth_rule_schema(self, schema, auth_rule_type):
        self.register_config_schema(schema, self.package + '_' + auth_rule_type)
        self.register_composite_config_schema(schema, auth_rule_type, exclude=['extension'])
    
    def get_current_config(self, event):
        config_id = event.request.POST.get('config_id')
        return self.get_config_by_id(config_id)


class BaseAuthRuleSchema(Schema):
    login_enabled: bool = Field(default=True, title=_('login_enabled', '启用登录'))
    register_enabled: bool = Field(default=True, title=_('register_enabled', '启用注册'))
    reset_password_enabled: bool = Field(default=True, title=_('reset_password_enabled', '启用重置密码'))
