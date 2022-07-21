
from .schema import *
from arkid.core.extension import create_extension_schema
from arkid.core.extension.impower_rule import ImpowerRuleBaseExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.models import User

ImpowerRuleCreateIn = create_extension_schema('ImpowerRuleCreateIn',__file__, base_schema=ImpowerRuleCreateIn)

class ImpowerRuleExtension(ImpowerRuleBaseExtension):

    def load(self):
        super().load()
        # 注册前端页面
        self.load_front_page()
        # 注册schema
        self.register_impower_rule_schema(ImpowerRuleCreateIn, 'DefaultImpowerRule')
    
    def load_front_page(self):
        '''
        注册前端页面
        '''
        self.register_front_pages(user_field_page)
        self.register_front_pages(app_page)
        self.register_front_pages(app_permission_page)

    def get_auth_result(self, event, **kwargs):
        '''
        获取权限鉴定结果
        '''
        data = event.data
        tenant = event.tenant

        user = data.get('user')
        config = data.get('config')
        # 处理授权逻辑
        permission_info = {}
        # 取得了所有配置
        config_info = config.config
        config_matchfield = config_info.get('matchfield')
        config_matchsymbol = config_info.get('matchsymbol')
        config_matchvalue = config_info.get('matchvalue')
        config_app = config_info.get('app')
        config_app_id = config_app.get('id')
        config_permissions = config_info.get('permissions')
        # 用户扩展字段用于筛选
        user = User.expand_objects.filter(id=user.id).first()
        # 选择的字段值
        select_value = user.get(config_matchfield.get('id'))
        # 取得返回值
        sort_ids = []
        if config_matchsymbol == '等于' and config_matchvalue == select_value:
            for config_permission in config_permissions:
                sort_ids.append(config_permission.get('sort_id'))
        return sort_ids

extension = ImpowerRuleExtension()