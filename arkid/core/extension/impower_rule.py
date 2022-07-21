from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig
from arkid.extension.models import Extension as Extension_Obj
from arkid.core import api as core_api, event as core_event

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
        self.listen_event(core_event.GET_AUTH_RESULT, self.get_auth_result)
    
    def get_extensions(self):
        '''
        获取当前类型所有的插件
        '''
        return Extension_Obj.active_objects.filter(
            package=self.package,
            type=self.TYPE
        ).all()
    
    def get_all_config(self, tenant_id):
        '''
        获取所有的配置
        '''
        return TenantExtensionConfig.active_objects.filter(
            tenant_id=tenant_id,
            extension__in=self.get_extensions()
        ).all()

    def register_impower_rule_schema(self, schema, impowerrule_type):
        """
        注册授权规则的schema
        Params:
            schema: schema
            impowerrule_type: 授权规则类型
        """
        self.register_config_schema(schema, self.package + '_' + impowerrule_type)
        self.register_composite_config_schema(schema, impowerrule_type, exclude=['extension'])

    @abstractmethod
    def get_auth_result(self, event, **kwargs):
        """
        抽象方法，获取权限的鉴定结果
        Params:
            event: 事件参数
                data: 数据
                    user: 用户
                    app: 应用(如果app是None，就表示这个应用是arkid)
                    arr: 权限结果数组(这个是已经赋值过分组权限的数据，有权限是1，没权限是0)
                tenant: 租户
            kwargs: 其它方法参数
        Return:
            arr: 授权结果数组
        """
        pass