
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
        app = data.get('app', None)
        arr = data.get('arr', [])
        # 处理授权逻辑
        configs = self.get_all_config(tenant.id)
        permission_infos = []
        # 取得了所有配置
        for config in configs:
            config_info = config.config
            config_matchfield = config_info.get('matchfield')
            config_matchsymbol = config_info.get('matchsymbol')
            config_matchvalue = config_info.get('matchvalue')
            config_app = config_info.get('app')
            config_app_id = config_app.get('id')
            config_permissions = config_info.get('permissions')
            if app is None:
                if config_app_id == 'arkid':
                    sort_ids = []
                    for config_permission in config_permissions:
                        sort_ids.append(config_permission.get('sort_id'))
                    permission_infos.append({
                        'matchfield': config_matchfield.get('id'),
                        'matchsymbol': config_matchsymbol,
                        'matchvalue': config_matchvalue,
                        'sort_ids': sort_ids
                    })
            else:
                app_id = str(app.id)
                if config_app_id == app_id:
                    sort_ids = []
                    for config_permission in config_permissions:
                        sort_ids.append(config_permission.sort_id)
                    permission_infos.append({
                        'matchfield': config_matchfield.get('sort_id'),
                        'matchsymbol': config_matchsymbol,
                        'matchvalue': config_matchvalue,
                        'sort_ids': sort_ids
                    })
        # 计算是否拥有权限
        sort_ids = []
        # 这里之所以要重新获取是因为扩展字段的筛选需要借助expand_objects
        user = User.expand_objects.filter(id=user.id).first()
        for permission_info in permission_infos:
            matchfield = permission_info.get('matchfield')
            matchsymbol = permission_info.get('matchsymbol')
            matchvalue = permission_info.get('matchvalue')
            select_value = user.get(matchfield)
            if matchsymbol == '等于' and matchvalue == select_value:
                sort_ids.extend(permission_info.get('sort_ids'))
        # 匹配的数据进行替换
        for index, value in enumerate(arr):
            if int(value) == 0 and index in sort_ids:
                arr[index] = 1
        return arr
        
extension = ImpowerRuleExtension()