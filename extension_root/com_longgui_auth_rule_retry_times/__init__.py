import uuid
from arkid.core import actions, pages
from arkid.core.event import Event, dispatch_event
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_factor import BaseAuthFactorSchema
from arkid.core.extension.auth_rule import AuthRuleExtension, BaseAuthRuleSchema,MainAuthRuleSchema
from arkid.core.translation import gettext_default as _
from ninja import Schema
from pydantic import Field
from .schema import *
from django.core.cache import cache
from arkid.core import event as core_event
class AuthRuleRetryTimesExtension(AuthRuleExtension):

    def load(self):
        super().load()
        self.create_extension_config_schema()
        
    def before_auth(self, event, **kwargs):
        pass

    def auth_success(self, event, **kwargs):
        pass

    def auth_fail(self, event, **kwargs):
        request_id = event.request.META.get('request_id')
        key = self.gen_key(request_id)
        try_times  = cache.get(key,0)
        cache.set(key,try_times+1)
    
    def login_page(self, event, **kwargs):
        request_id = event.request.META.get('request_id')
        key = self.gen_key(request_id)
        try_times  = cache.get(key,0)
        
        auth_factor_config = event.data.get("auth_factor_config")
        title = event.data.get("title")
        items = event.data.get("items")
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == auth_factor_config.id.hex:
                dispatch_event(Event(tag=f"{config.config['second_auth_factor']['package']}.fix_login_page", tenant=event.tenant, request=event.request,  data={"items":items,"title":title}))
    
    def gen_key(self,request_id:str):
        return f"{self.package}_cache_{request_id}"
    
    def create_extension_config_schema(self):
        main_auth_factor_page = pages.TablePage(select=True,name=_("选择主认证因素"))

        self.register_front_pages(main_auth_factor_page)

        main_auth_factor_page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenants/{tenant_id}/config_select/?extension__type=auth_factor',
                method=actions.FrontActionMethod.GET
                
            )
        )
        
        second_auth_factor_page = pages.TablePage(select=True,name=_("选择次认证因素"))

        self.register_front_pages(second_auth_factor_page)

        second_auth_factor_page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenants/{tenant_id}/config_select/?extension__type=auth_factor',
                method=actions.FrontActionMethod.GET
            )
        )
        
        AuthRuleRetryTimesConfigSchema = create_extension_schema(
            'AuthRuleRetryTimesConfigSchema',
            __file__,
            [
                (
                    'try_times', 
                    int, 
                    Field(
                        title=_('try_times', '限制重试次数'),
                        default=3
                    )
                ),
                (
                    'main_auth_factor',
                    MainAuthRuleSchema, 
                    Field(
                        title=_('main_auth_factor', '主认证因素'),
                        page=main_auth_factor_page.tag
                    )
                ),
                (
                    'second_auth_factor',
                    SecondAuthFactorConfigSchema,
                    Field(
                        title=_('second_auth_factor', '次认证因素'),
                        page=second_auth_factor_page.tag
                    )
                ),
            ],
            base_schema=BaseAuthRuleSchema
        )
        self.register_auth_rule_schema(
            AuthRuleRetryTimesConfigSchema,
            "retry_times"
        )

extension = AuthRuleRetryTimesExtension()
