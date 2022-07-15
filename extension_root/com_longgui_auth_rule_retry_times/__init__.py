import uuid
from api.v1.views.loginpage import login_page
from arkid.core import actions, pages
from arkid.core.event import AUTH_FAIL, Event, dispatch_event,BEFORE_AUTH
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_factor import BaseAuthFactorSchema
from arkid.core.extension.auth_rule import AuthRuleExtension, BaseAuthRuleSchema,MainAuthRuleSchema
from arkid.core.translation import gettext_default as _
from ninja import Schema
from pydantic import Field
from .error import ErrorCode
from .schema import *
from django.core.cache import cache
from arkid.core import event as core_event
class AuthRuleRetryTimesExtension(AuthRuleExtension):

    def load(self):
        super().load()
        self.create_extension_config_schema()
        self.listen_event(AUTH_FAIL,self.auth_fail)
        self.listen_event(BEFORE_AUTH,self.before_auth)
        
    def before_auth(self,event,**kwargs):
        """ 响应事件：认证之前, 判断是否满足次级认证因素校验条件，如满足则触发事件并检查次级认证因素校验结果

        Args:
            event: 事件

        Returns:
            tuple(bool,dict): 次级认证因素校验结果
        """
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == event.data["auth_factor_config_id"]:
                host = event.request.META.get("REMOTE_ADDR")
                if self.check_retry_times(host,config.id.hex,config.config.get("try_times",0)):
                    # 判定需要验证
                    responses = dispatch_event(
                        Event(
                            core_event.AUTHRULE_CHECK_AUTH_DATA,
                            tenant=event.tenant,
                            request=event.request,
                            packages=[
                                config.config["second_auth_factor"]["package"]
                            ]
                        )
                    )
                    
                    for useless,(response,useless) in responses:
                        if not response:
                            continue
                        result,data = response
                        if not result:
                            return response
        return True,None
        
    def auth_fail(self, event, **kwargs):
        """响应事件：认证失败，记录对应IP认证失败次数

        Args:
            event : 事件
        """
        data = event.data["data"]
        # 检查是否存在满足条件的配置
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == event.data["auth_factor_config_id"]:
                host = event.request.META.get("REMOTE_ADDR")
                key = self.gen_key(host,config.id.hex)
                try_times  = cache.get(key,0)
                cache.set(key,try_times+1)
                if self.check_retry_times(host,config.id.hex,config.config.get("try_times",0)) and not self.check_refresh_status(host,config.id.hex):
                    data.update(self.error(ErrorCode.AUTH_FAIL_TIMES_OVER_LIMITED))
                    self.set_refresh_status(host,config.id.hex)
                    data["refresh"] = True
                    

    def check_rule(self, event, config):
        login_pages = event.data
        
        if self.check_retry_times(event.request.META.get("REMOTE_ADDR"),config.id.hex,config.config.get("try_times",0)): 
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
            
    def check_retry_times(self,host,config_id,limited=3):
        """校验认证失败次数是否超出限制

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID
            limited (int, optional): 认证失败次数限制. Defaults to 3.

        Returns:
            bool: 校验结果
        """
        key=self.gen_key(host,config_id)
        retry_times = cache.get(key,0)
        return retry_times > limited
    
    def set_refresh_status(self,host,config_id):
        """设置登陆页面刷新tag

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID
        """
        cache.set(self.gen_refresh_key(host,config_id),1)
    
    def check_refresh_status(self,host,config_id):
        """校验是否需要刷新页面

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID

        Returns:
            bool: 是否需要刷新页面
        """
        return bool(cache.get(self.gen_refresh_key(host,config_id),0))
        
    def gen_refresh_key(self,host:str,config_id:str):
        """页面刷新标识KEY

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID

        Returns:
            str: 页面刷新标识KEY
        """
        return f"{self.package}_cache_auth_refresh_{host}_{config_id}"
    
    def gen_key(self,host:str,config_id:str):
        """生成记录失败次数的KEY

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID

        Returns:
            str: 记录失败次数的KEY
        """
        return f"{self.package}_cache_auth_retry_times_{host}_{config_id}"
    
    def create_extension_config_schema(self):
        """创建插件运行时schema
        """
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
