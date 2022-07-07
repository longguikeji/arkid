
from .schema import *
from arkid.core.extension import create_extension_schema
from arkid.core.extension.impower_rule import ImpowerRuleBaseExtension

ImpowerRuleCreateIn = create_extension_schema('ImpowerRuleCreateIn',__file__, base_schema=ImpowerRuleCreateIn)

class ImpowerRuleExtension(ImpowerRuleBaseExtension):

    def load(self):
        super().load()
        # 注册前端页面
        self.load_front_page()
        # 注册schema
        self.register_impowerrule_schema(ImpowerRuleCreateIn, 'DefaultImpowerRule')
    
    def load_front_page(self):
        '''
        注册前端页面
        '''
        self.register_front_pages(app_page)
        self.register_front_pages(app_permission_page)

    def create_rule(self, event, **kwargs):
        pass

    def update_rule(self, event, **kwargs):
        pass

    def delete_rule(self, event, **kwargs):
        pass
        
extension = ImpowerRuleExtension()