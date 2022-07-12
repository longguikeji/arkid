import uuid
from api.v1.views.loginpage import login_page
from arkid.core import actions, pages
from arkid.core.event import AUTH_FAIL, Event, dispatch_event
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
        self.listen_event(AUTH_FAIL,self.auth_fail)
        
    def auth_fail(self, event, **kwargs):
        request_id = event.request.META.get('request_id')
        key = self.gen_key(request_id)
        try_times  = cache.get(key,0)
        cache.set(key,try_times+1)
    
    def check_rule(self, event, config):
        # 判断规则是否通过 如通过则执行对应操作
        login_pages = event.data
        
        # TODO 判断规则
        
        if True: 
            dispatch_event(
                Event(
                    core_event.AUTHRULE_FIX_LOGIN_PAGE,
                    tenant=event.tenant,
                    request=event.request,
                    packages=[
                        config.config["second_auth_factor"]["package"]
                    ],
                    data={
                        "login_pages": login_pages,
                        "main_auth_factor_id": config.config["main_auth_factor"]["id"],
                        "config_id":config.config["second_auth_factor"]["id"]
                    }
                )
            )
        
    
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
