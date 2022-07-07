from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig

class ImpowerRuleBaseExtension(Extension):

    TYPE = 'impower_rule'

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig

    @property
    def type(self):
        return ImpowerRuleBaseExtension.TYPE

    def load(self):
        super().load()

    def register_impowerrule_schema(self, schema, impowerrule_type):
        """
        注册授权规则的schema
        Params:
            schema: schema
            impowerrule_type: 授权规则类型
        """
        self.register_config_schema(schema, self.package + '_' + impowerrule_type)
        self.register_composite_config_schema(schema, impowerrule_type, exclude=['extension'])

    @abstractmethod
    def create_rule(self, event, **kwargs):
        """
        抽象方法，创建授权规则
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass

    @abstractmethod
    def update_rule(self, event, **kwargs):
        """
        抽象方法，修改授权规则
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass

    @abstractmethod
    def delete_rule(self, event, **kwargs):
        """
        抽象方法，删除授权规则
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass