import json
from django.urls import reverse
from arkid.core.constants import *
from arkid.core.api import GlobalAuth, operation
from arkid.core.event import SEND_SMS, Event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.common.logger import logger
from arkid.extension.models import TenantExtensionConfig
from .error import ErrorCode
from arkid.core.models import User
from .sms import check_sms_code, create_sms_code,gen_sms_code
from arkid.core import actions, pages
from .models import UserMobile
from pydantic import Field
from typing import List, Optional
from arkid.core.translation import gettext_default as _
from django.db import transaction
from arkid.core.extension import create_extension_schema
from .schema import *
from django.contrib.auth.hashers import (
    make_password,
)

class MobileAuthFactorExtension(AuthFactorExtension):
    """手机短信验证码认证因素插件
    """
    def load(self):
        """加载插件
        """
        super().load()
        
        self.create_extension_config_schema()
        
        self.register_extend_field(UserMobile, "mobile")
        from api.v1.schema.auth import AuthIn
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut
        self.register_extend_api(
            AuthIn,
            UserCreateIn, 
            UserItemOut, 
            UserUpdateIn, 
            UserListItemOut,
            mobile=(Optional[str],Field(title=_("电话号码"))),
            # areacode=(str,Field(title=_("区号")))
        )
        self.register_extend_api(
            ProfileSchemaOut, 
            mobile=(Optional[str],Field(readonly=True))
        )
        
        # 注册发送短信接口
        self.url_send_sms_code = self.register_api(
            '/config/{config_id}/send_sms_code/',
            'POST',
            self.send_sms_code,
            tenant_path=True,
            auth=None,
            response=SendSMSCodeOut,
        )
        print(self.url_send_sms_code)
    
    def authenticate(self, event, **kwargs):
        """ 认证
        
        通过手机号码查找用户并校验短信验证码

        Args:
            event (Event): 事件

        """
        tenant = event.tenant
        request = event.request
        data = request.POST or json.load(request.body)
        
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')

        # user = User.expand_objects.filter(tenant=tenant,mobile=mobile)
        temp_users = tenant.users.all()
        user_ids = []
        for temp_user in temp_users:
            user_ids.append(temp_user.id)
        user = User.expand_objects.filter(
            is_active=True,
            is_del=False,
            id__in=user_ids,
            mobile=mobile
        )
        if len(user) > 1:
            logger.error(f'{mobile}在数据库中匹配到多个用户')
            return self.auth_failed(event, data=self.error(ErrorCode.CONTACT_MANAGER))
        if user:
            user = user[0]
            if check_sms_code(tenant, mobile, sms_code):
                user = User.active_objects.get(id=user.get("id"))
                return self.auth_success(user,event)
            else:
                msg = ErrorCode.SMS_CODE_MISMATCH
        else:
            msg = ErrorCode.MOBILE_NOT_EXISTS_ERROR
        return self.auth_failed(event, data=self.error(msg))

    @transaction.atomic()
    def register(self, event, **kwargs):
        """ 注册用户

        Args:
            event (Event): 事件
        """
        tenant = event.tenant
        request = event.request
        data = request.POST or json.load(request.body)
        
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        username = data.get('username')

        config = self.get_current_config(event)
        ret, message = self.check_mobile_exists(mobile, tenant)
        if not ret:
            return self.error(message)
        
        if not check_sms_code(tenant, mobile, sms_code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)
        
        ret, message = self.check_username_exists(username, tenant)
        if not ret:
            return self.error(message)
        
        user = User(tenant=tenant)

        user.mobile = mobile
        user.username = username
        
        user.save()
        tenant.users.add(user)
        tenant.save()

        return user

    def reset_password(self, event, **kwargs):
        """ 重置密码

        Args:
            event (Event): 事件
        """
        tenant = event.tenant
        request = event.request
        data = request.POST or json.load(request.body)
        
        mobile = data.get('mobile')
        sms_code = data.get('sms_code')
        
        password = data.get('password')
        checkpassword = data.get('checkpassword')
        
        if password != checkpassword:
            return self.error(ErrorCode.PASSWORD_IS_INCONSISTENT)
                
        if not check_sms_code(tenant, mobile, sms_code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)
        
        # user = User.expand_objects.filter(tenant=tenant,mobile=mobile)
        temp_users = tenant.users.all()
        user_ids = []
        for temp_user in temp_users:
            user_ids.append(temp_user.id)
        user = User.expand_objects.filter(
            is_active=True,
            is_del=False,
            id__in=user_ids,
            mobile=mobile
        )
        if len(user) > 1:
            logger.error(f'{mobile}在数据库中匹配到多个用户')
            return self.error(ErrorCode.CONTACT_MANAGER)
        if user:
            user = user[0]
            user.password = make_password(password)
            user.save()
            return self.success()
        
        return self.error(ErrorCode.MOBILE_NOT_EXISTS_ERROR)

    def create_login_page(self, event, config, config_data):
        """ 生成手机验证码登录页面Schema描述

        Args:
            event (Event): 事件
            config (TenantExtensionConfig): 插件运行时配置
        """
        
        items = [
            {
                "type": "text",
                "name":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_sms_code,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "areacode": "86",
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name":"sms_code",
                "placeholder": "验证码",
            }
        ]
        self.add_page_form(config, self.LOGIN, "手机验证码登录", items, config_data)

    def create_register_page(self, event, config, config_data):
        """生成手机验证码用户注册页面Schema描述

        因本插件提供重置密码功能，此处需用户指定账号用户名

        Args:
            event (Event): 事件
            config (TenantExtensionConfig): 插件运行时配置
        """
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": "用户名"
            },
            {
                "type": "text",
                "name":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_sms_code,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "areacode": "86",
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name":"sms_code",
                "placeholder": "验证码"
            }
        ]
        self.add_page_form(config, self.REGISTER, "手机验证码注册", items, config_data)

    def create_password_page(self, event, config, config_data):
        """生成重置密码页面Schema描述
        
        通过手机验证码重置密码时需提供手机号码以及对应验证码，同时此处添加新密码确认机制
        
        注意：重置密码功能需要启用用户名密码认证插件以提供完整支持

        Args:
            event (Event): 事件
            config (TenantExtensionConfig): 插件运行时配置
        """
        items = [
            {
                "type": "text",
                "name":"mobile",
                "placeholder": "手机号码",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_sms_code,
                        "method": "post",
                        "params": {
                            "mobile": "mobile",
                            "areacode": "86",
                        },
                    },
                }
            },
            {
                "type": "text",
                "name":"sms_code",
                "placeholder": "验证码"
            },
            {
                "type": "password",
                "name":"password",
                "placeholder": "密码"
            },
            {
                "type": "password",
                "name":"checkpassword",
                "placeholder": "密码确认"
            }
        ]
        self.add_page_form(config, self.RESET_PASSWORD, "手机验证码重置密码", items, config_data)

    def create_other_page(self, event, config, config_data):
        """创建其他页面（本插件无相关页面）

        Args:
            event (Event): 事件
            config (TenantExtensionConfig): 插件运行时配置
        """
        pass
    
    def check_mobile_exists(self, mobile, tenant):
        """检查电话号码是否已存在

        Args:
            mobile (str): 手机号
            tenant (Tenant): 租户

        Returns:
            (bool,ErrorCode): mobile是否存在以及对应错误
        """
        if not mobile:
            return False, ErrorCode.MOBILE_EMPTY
        # 需要临时存储
        temp_users = tenant.users.all()
        user_ids = []
        for temp_user in temp_users:
            user_ids.append(temp_user.id)
        if User.expand_objects.filter(
            is_active=True,
            is_del=False,
            id__in=user_ids,
            mobile=mobile
        ).count():
        # if User.expand_objects.filter(tenant=tenant,mobile=mobile).count():
            return False, ErrorCode.MOBILE_EXISTS_ERROR
        return True, None
    
    def check_username_exists(self,username,tenant):
        """检查用户名是否已存在

        Args:
            username (str): 用户名
            tenant (Tenant): 租户

        Returns:
            (bool,ErrorCode): username是否存在以及对应错误
        """
        # 检查username是否为空
        if not username:
            return False, ErrorCode.USERNAME_EMPTY
        # 检查username是否已存在
        if tenant.users.filter(is_active=True, is_del=False).filter(username=username).count():
        # if User.expand_objects.filter(tenant=tenant,username=username).count():
            return False, ErrorCode.USERNAME_EXISTS_ERROR
        
        return True, None

    def check_auth_data(self, event, **kwargs):
        pass

    def fix_login_page(self, event, **kwargs):
        pass
    
    def create_auth_manage_page(self):
        """ 创建“我的-认证管理”中的更换手机号码页面
        """
        _pages = []
        
        mine_mobile_path = self.register_api(
            "/mine_mobile/",
            "GET",
            self.mine_mobile,
            tenant_path=True,
            auth=GlobalAuth(),
            response=MineMobileOut
        )
        
        upodate_mine_mobile_path = self.register_api(
            "/mine_mobile/",
            'POST',
            self.update_mine_mobile,
            tenant_path=True,
            auth=GlobalAuth(),
            response=UpdateMineMobileOut
        )
        
        name = '更改手机号码'

        page = pages.FormPage(name=name)
        page.create_actions(
            init_action=actions.DirectAction(
                path=mine_mobile_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=upodate_mine_mobile_path
                ),
            }
        )
        
        _pages.append(page)
        return _pages

    def create_extension_config_schema(self):
        """创建插件运行时配置schema描述
        """
        select_sms_page = pages.TablePage(select=True,name=_("指定短信插件运行时"))

        self.register_front_pages(select_sms_page)

        select_sms_page.create_actions(
            init_action=actions.DirectAction(
                path='/api/v1/tenants/{tenant_id}/config_select/?extension__type=sms',
                method=actions.FrontActionMethod.GET
            )
        )
        
        MobileAuthFactorSchema = create_extension_schema(
            'MobileAuthFactorSchema',
            __file__, 
            [
                (
                    'sms_config', 
                    MobileAuthFactorConfigSchema, 
                    Field(
                        title=_('sms extension config', '短信插件运行时'),
                        page=select_sms_page.tag,
                    ),
                ),
                (
                    'code_length', 
                    int, 
                    Field(
                        title=_('code_length', '验证码长度'),
                        default=6
                    )
                ),
                (
                    'expired', 
                    Optional[int],
                    Field(
                        title=_('expired', '有效期/分钟'),
                        default=10,
                    )
                ),
            ],
            BaseAuthFactorSchema,
        )
        self.register_auth_factor_schema(MobileAuthFactorSchema, 'mobile')
    
    @operation(SendSMSCodeOut)
    def send_sms_code(self,request,tenant_id,config_id:str,data:SendSMSCodeIn):
        """发送短信验证码
        """
        tenant = request.tenant
        mobile = data.mobile
        config = self.get_config_by_id(config_id)
        if not config:
            return self.error(ErrorCode.CONFIG_IS_NOT_EXISTS)
        
        if not mobile or mobile=="mobile":
            return self.error(ErrorCode.MOBILE_EMPTY)
        
        code = create_sms_code(tenant,mobile,config.config.get('code_length',6),config.config.get("expired",10)*60)

        
        responses = dispatch_event(
            Event(
                tag=SEND_SMS,
                tenant=tenant,
                request=request,
                data={
                    "config_id":config.config["sms_config"]["id"],
                    "mobile":data.mobile,
                    "code": code,
                    "areacode": data.areacode,
                    "username": request.user.username if request.user else ""
                },
                packages=config.config["sms_config"]["package"]
                
            )
        )
        
        if not responses:
            return self.error(ErrorCode.SMS_EXTENSION_NOT_EXISTS)
        useless, (data, extension) = responses[0]
        if data:
            return self.success()
        else:
            return self.error(ErrorCode.SMS_SEND_FAILED)

    @operation(UpdateMineMobileOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def update_mine_mobile(self, request, tenant_id: str,data:UpdateMineMobileIn):
        """ 普通用户：更新手机号码
        """
        mobile = data.mobile
        ret, message = self.check_mobile_exists(mobile, request.tenant)
        if not ret:
            return self.error(message)
        
        if not check_sms_code(request.tenant,mobile,data.code):
            return self.error(ErrorCode.SMS_CODE_MISMATCH)
        
        user = request.user
        user.mobile=data.mobile
        user.save()
        
        return self.success()
    
    @operation(MineMobileOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def mine_mobile(self,request,tenant_id: str):
        user = request.user
        user_expand = User.expand_objects.filter(id=user.id).first()
        
        config = self.get_tenant_configs(request.tenant).first()
        
        if not config:
            return self.error(
                ErrorCode.CONFIG_IS_NOT_EXISTS
            )
        
        return self.success(
            data={
                "current_mobile": user_expand.get("mobile",None),
                "mobile": "",
                "code": "",
                "config_id": config.id.hex,
            },
        )

    
extension = MobileAuthFactorExtension()
