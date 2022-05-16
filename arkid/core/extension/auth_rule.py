
from abc import abstractmethod
from enum import Enum
from ninja import Schema
from pydantic import Field
from arkid.core.extension import Extension
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

        # 认证前规则
        self.listen_event("api_v1_views_auth_auth_pre", self.before_auth)

        self.listen_event("api_v1_views_auth_auth", self.after_auth)

    def after_auth(self,event,**kwargs):
        if event.response["error"]:
            self.auth_fail(event,**kwargs)
        else:
            self.auth_success(event,**kwargs)

    @abstractmethod
    def auth_success(self, event, **kwargs):
        """ 认证成功规则
        """
        pass

    @abstractmethod
    def auth_fail(self, event, **kwargs):
        """ 认证失败规则
        """
        pass

    @abstractmethod
    def before_auth(self, event, **kwargs):
        """ 认证前规则
        """
        pass

    def register_auth_rule_schema(self, schema, auth_rule_type):
        self.register_config_schema(schema, self.package + '_' + auth_rule_type)
        self.register_composite_config_schema(schema, auth_rule_type, exclude=['extension'])
    
    def get_current_config(self, event):
        config_id = event.request.POST.get('config_id')
        return self.get_config_by_id(config_id)


class BaseAuthRuleSchema(Schema):
    main_auth_factor: str = Field(title=_('main_auth_factor', '主认证因素'))