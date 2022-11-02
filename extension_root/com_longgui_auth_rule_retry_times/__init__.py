from typing import Optional
import uuid
from api.v1.views.loginpage import login_page
from arkid.common.utils import get_remote_addr
from arkid.core import actions, pages
from arkid.core.event import AUTH_FAIL, AUTH_SUCCESS, Event, dispatch_event,BEFORE_AUTH
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_factor import BaseAuthFactorSchema
from arkid.core.extension.auth_rule import AuthRuleExtension, BaseAuthRuleSchema,MainAuthRuleSchema
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from ninja import Schema
from pydantic import Field

from arkid.extension.models import TenantExtensionConfig,Extension
from .error import ErrorCode
from .schema import *
from arkid.common import cache
from arkid.core import event as core_event
class AuthRuleRetryTimesExtension(AuthRuleExtension):

    def load(self):
        super().load()
        self.create_extension_config_schema()
        self.listen_event(AUTH_FAIL,self.auth_fail)
        self.listen_event(BEFORE_AUTH,self.before_auth)
        self.listen_event(AUTH_SUCCESS,self.auth_success)
        
        # 配置初始数据
        tenant = Tenant.platform_tenant()
        if not self.get_tenant_configs(tenant):
            main_auth_factor = TenantExtensionConfig.active_objects.filter(
                tenant=tenant,
                extension=Extension.active_objects.filter(
                    package="com.longgui.auth.factor.password"
                ).first(),
                type="password"
            ).first()
            
            second_auth_factor = TenantExtensionConfig.active_objects.filter(
                tenant=tenant,
                extension=Extension.active_objects.filter(
                    package="com.longgui.auth.factor.authcode"
                ).first(),
                type="authcode"
            ).first()
            
            if main_auth_factor and second_auth_factor:
                # 如主认证因素和此认证因素都存在的情况下 创建认证规则
                
                config = {
                    "main_auth_factor": {
                        "id": main_auth_factor.id.hex, 
                        "name": main_auth_factor.name, 
                        "package": main_auth_factor.extension.package
                    }, 
                    "second_auth_factor": {
                        "id": second_auth_factor.id.hex, 
                        "name": second_auth_factor.name, 
                        "package": second_auth_factor.extension.package
                    }, 
                    "try_times": 3
                }
                self.create_tenant_config(tenant, config, "认证规则:登录失败三次启用图形验证码", "retry_times")
        
    def before_auth(self,event,**kwargs):
        """ 响应事件：认证之前, 判断是否满足次级认证因素校验条件，如满足则触发事件并检查次级认证因素校验结果

        Args:
            event: 事件

        Returns:
            tuple(bool,dict): 次级认证因素校验结果
        """
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == event.data["auth_factor_config_id"]:
                host = get_remote_addr(event.request)
                if self.check_retry_times(event.tenant,host,config.id.hex,config.config.get("try_times",0)):
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
    
    def auth_success(self,event,**kwargs):
        # 检查是否存在满足条件的配置
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == event.data["auth_factor_config_id"].id.hex:
                host = get_remote_addr(event.request)
                key = self.gen_key(host,config.id.hex)
                try_times  = 1
                cache.set(event.tenant,key,try_times,expired=config.config.get("expired",30)*60)
                self.clear_refresh_status(event.tenant,host,config.id.hex)
        
    def auth_fail(self, event, **kwargs):
        """响应事件：认证失败，记录对应IP认证失败次数

        Args:
            event : 事件
        """
        data = event.data["data"]
        # 检查是否存在满足条件的配置
        for config in self.get_tenant_configs(event.tenant):
            if uuid.UUID(config.config["main_auth_factor"]["id"]).hex == event.data["auth_factor_config_id"]:
                host = get_remote_addr(event.request)
                key = self.gen_key(host,config.id.hex)
                try_times  = int(cache.get(event.tenant,key) or 1)
                cache.set(event.tenant,key,try_times+1,expired=config.config.get("expired",30)*60)
                if self.check_retry_times(event.tenant,host,config.id.hex,config.config.get("try_times",0)) and not self.check_refresh_status(event.tenant,host,config.id.hex):
                    data.update(self.error(ErrorCode.AUTH_FAIL_TIMES_OVER_LIMITED))
                    self.set_refresh_status(event.tenant,host,config.id.hex)
                    data["refresh"] = True
                    

    def check_rule(self, event, config):
        login_pages = event.data
        
        if self.check_retry_times(event.tenant,get_remote_addr(event.request),config.id.hex,config.config.get("try_times",0)): 
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
            
    def check_retry_times(self,tenant,host,config_id,limited=3):
        """校验认证失败次数是否超出限制

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID
            limited (int, optional): 认证失败次数限制. Defaults to 3.

        Returns:
            bool: 校验结果
        """
        key=self.gen_key(host,config_id)
        retry_times = int(cache.get(tenant,key) or limited)
        return retry_times > limited
    
    def set_refresh_status(self,tenant,host,config_id):
        """设置登陆页面刷新tag

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID
        """
        cache.set(tenant,self.gen_refresh_key(host,config_id),1)
        
    def clear_refresh_status(self,tenant,host,config_id):
        cache.set(tenant,self.gen_refresh_key(host,config_id),0)
    
    def check_refresh_status(self,tenant,host,config_id):
        """校验是否需要刷新页面

        Args:
            host (str): 客户一端IP地址
            config_id (str): 插件运行时ID

        Returns:
            bool: 是否需要刷新页面
        """
        return bool(cache.get(tenant,self.gen_refresh_key(host,config_id)))
        
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
                (
                    'expired', 
                    Optional[int],
                    Field(
                        title=_('expired', '有效期/分钟'),
                        default=30,
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
