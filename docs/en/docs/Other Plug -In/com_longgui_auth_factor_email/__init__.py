
from asyncio.log import logger
from email.utils import formataddr
import json
import re
from typing_extensions import Self

from django.conf import settings
from arkid.config import get_app_config
from django.db import transaction
from arkid.core.api import GlobalAuth, operation
from arkid.core.error import ErrorDict, SuccessDict
from arkid.core.event import Event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.models import User,UserGroup
from arkid.core.token import refresh_token
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.constants import *
from arkid.core import pages,actions, routers
from arkid.core.translation import gettext_default as _
from .schema import *
from .error import ErrorCode
from .models import *
from .email import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from django.contrib.auth.hashers import (
    make_password,
)

class EmailAuthFactorExtension(AuthFactorExtension):
    
    def load(self):
        super().load()
        self.register_extension_api()
        self.register_extension_config_schema()
        
        self.register_extend_field(UserEmail, "email")
        from api.v1.schema.auth import AuthIn
        from api.v1.schema.user import UserCreateIn,UserItemOut,UserUpdateIn,UserListItemOut
        from api.v1.schema.mine import ProfileSchemaOut
        self.register_extend_api(
            AuthIn,
            UserCreateIn, 
            UserItemOut, 
            UserUpdateIn, 
            UserListItemOut,
            email=(Optional[str],Field(title=_("邮箱"))),
            # areacode=(str,Field(title=_("区号")))
        )
        self.register_extend_api(
            ProfileSchemaOut, 
            email=(Optional[str],Field(readonly=True))
        )
    
    def register_extension_api(self):
        """注册插件所需API
        """
        self.url_send_email_code = self.register_api(
            '/config/{config_id}/send_email_code/',
            'POST',
            self.send_email_code,
            tenant_path=True,
            auth=None,
            response=SendEmailCodeOut,
        )
    
    def register_extension_config_schema(self):
        """注册认证因素配置
        """
        EmailAuthFactorSchema = create_extension_schema(
            "EmailAuthFactorSchema",
            __file__, 
            [
                (
                    'smtp_host', 
                    str, 
                    Field(
                        title=_('smtp_host', 'SMTP服务地址'),
                    )
                ),
                (
                    'smtp_port', 
                    str, 
                    Field(
                        title=_('smtp_port', 'SMTP服务端口'),
                    )
                ),
                (
                    'smtp_username', 
                    str, 
                    Field(
                        title=_('smtp_username', 'SMTP服务账号'),
                    )
                ),
                (
                    'smtp_password', 
                    str, 
                    Field(
                        title=_('smtp_password', 'SMTP服务密码'),
                    )
                ),
                (
                    'smtp_subject', 
                    Optional[str], 
                    Field(
                        title=_('smtp_subject', '邮件标题'),
                        default="您的短信验证码"
                    )
                ),
                (
                    'smtp_from', 
                    Optional[str], 
                    Field(
                        title=_('smtp_from', '发送者名称'),
                        default="龙归科技"
                    )
                ),
                (
                    'smtp_to', 
                    Optional[str], 
                    Field(
                        title=_('smtp_to', '接收者名称'),
                        default="Arkid平台用户"
                    )
                ),
                (
                    'smtp_template', 
                    Optional[str], 
                    Field(
                        title=_('smtp_template', '邮件模板'),
                        default="您的短信验证码是{code}"
                    )
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
                        default=10
                    )
                ),
            ],
            BaseAuthFactorSchema,
        )
        
        self.register_auth_factor_schema(
            EmailAuthFactorSchema,
            "email"
        )
    
    def authenticate(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        data = request.POST or json.load(request.body)
        
        email = data.get('email')
        email_code = data.get('code')

        user = User.expand_objects.filter(tenant=tenant,email=email)
        if len(user) > 1:
            logger.error(f'{email}在数据库中匹配到多个用户')
            return self.auth_failed(event, data=self.error(ErrorCode.CONTACT_MANAGER))
        if user:
            user = user[0]
            if check_email_code(tenant, email, email_code):
                user = User.active_objects.get(id=user.get("id"))
                return self.auth_success(user,event)
            else:
                msg = ErrorCode.EMAIL_CODE_MISMATCH
        else:
            msg = ErrorCode.EMAIL_NOT_EXISTS_ERROR
        return self.auth_failed(event, data=self.error(msg))
    
    def check_auth_data(self, event, **kwargs):
        return super().check_auth_data(event, **kwargs)
    
    def create_auth_manage_page(self):
        
        _pages = []
        
        mine_email_path = self.register_api(
            "/mine_email/",
            "GET",
            self.mine_email,
            tenant_path=True,
            auth=GlobalAuth(),
            response=MineEmailOut
        )
        
        upodate_mine_email_path = self.register_api(
            "/mine_email/",
            'POST',
            self.update_mine_email,
            tenant_path=True,
            auth=GlobalAuth(),
            response=UpdateMineEmailOut
        )
        
        name = '更改邮箱'

        page = pages.FormPage(name=name)
        page.create_actions(
            init_action=actions.DirectAction(
                path=mine_email_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=upodate_mine_email_path
                ),
            }
        )
        
        _pages.append(page)
        return _pages
    
    def create_login_page(self, event, config, config_data):
        items = [
            {
                "type": "text",
                "name":"email",
                "placeholder": "邮箱",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_email_code,
                        "method": "post",
                        "params": {
                            "email": "email",
                            "areacode": "86",
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name":"code",
                "placeholder": "验证码",
            }
        ]
        self.add_page_form(config, self.LOGIN, "邮箱验证码登录", items, config_data)
        
        return super().create_login_page(event, config, config_data)
    
    def create_other_page(self, event, config, config_data):
        return super().create_other_page(event, config, config_data)
    
    def create_password_page(self, event, config, config_data):
        items = [
            {
                "type": "text",
                "name":"email",
                "placeholder": "邮箱",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_email_code,
                        "method": "post",
                        "params": {
                            "email": "email",
                            "areacode": "86",
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name":"code",
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
        self.add_page_form(config, self.RESET_PASSWORD, "邮箱验证码重置密码", items, config_data)
    
    def create_register_page(self, event, config, config_data):
        items = [
            {
                "type": "text",
                "name": "username",
                "placeholder": "用户名"
            },
            {
                "type": "text",
                "name":"email",
                "placeholder": "邮箱",
                "append": {
                    "title": "发送验证码",
                    "http": {
                        "url": self.url_send_email_code,
                        "method": "post",
                        "params": {
                            "email": "email",
                            "areacode": "86",
                        },
                    },
                    "delay": 60
                }
            },
            {
                "type": "text",
                "name":"code",
                "placeholder": "验证码"
            }
        ]
        self.add_page_form(config, self.REGISTER, "邮箱验证码注册", items, config_data)
    
    def fix_login_page(self, event, **kwargs):
        return super().fix_login_page(event, **kwargs)
    
    @transaction.atomic()
    def register(self, event, **kwargs):
        """ 注册用户

        Args:
            event (Event): 事件
        """
        tenant = event.tenant
        request = event.request
        data = request.POST or json.load(request.body)
        
        email = data.get('email')
        code = data.get('code')
        username = data.get('username')

        config = self.get_current_config(event)
        ret, message = self.check_email_exists(email, tenant)
        if not ret:
            return self.error(message)
        
        if not check_email_code(email, code):
            return self.error(ErrorCode.EMAIL_CODE_MISMATCH)
        
        ret, message = self.check_username_exists(username, tenant)
        if not ret:
            return self.error(message)
        
        user = User(tenant=tenant)

        user.email = email
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
        
        email = data.get('email')
        email_code = data.get('code')
        
        password = data.get('password')
        checkpassword = data.get('checkpassword')
        
        if password != checkpassword:
            return self.error(ErrorCode.PASSWORD_IS_INCONSISTENT)
                
        if not check_email_code(email, email_code):
            return self.error(ErrorCode.EMAIL_CODE_MISMATCH)
        
        user = User.expand_objects.filter(tenant=tenant,email=email)
        
        if len(user) > 1:
            logger.error(f'{email}在数据库中匹配到多个用户')
            return self.error(ErrorCode.CONTACT_MANAGER)
        if user:
            user = user[0]
            user = User.active_objects.get(id=user.get("id"))
            user.password = make_password(password)
            user.save()
            return self.success()
        
        return self.error(ErrorCode.EMAIL_NOT_EXISTS_ERROR)
    
    def send_email_code(self,request,tenant_id,config_id:str,data:SendEmailCodeIn):
        """发送短信验证码
        """
        tenant = request.tenant
        config = self.get_config_by_id(config_id)
        if not config:
            return self.error(ErrorCode.CONFIG_IS_NOT_EXISTS)
        
        expired = config.config.get('expired',None)
        if expired:
            expired = expired*60
        
        code = create_email_code(tenant,data.email,config.config.get("code_length",6),expired)
        email = data.email
        
        if not email or email=="email":
            return self.error(ErrorCode.EMAIL_EMPTY)
        
        sender = config.config.get("smtp_username")
        receivers = email  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
        
        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        message = MIMEText(config.config.get("smtp_template").replace("{code}",code), 'plain', 'utf-8')
        message['From'] = formataddr([config.config.get("smtp_from","龙归科技"),sender])  # 发送者
        message['To'] =  formataddr([config.config.get("smtp_to","Arkid平台用户"),receivers])        # 接收者
        
        subject = config.config.get("smtp_subject",'您的验证码已送达')
        message['Subject'] = Header(subject, 'utf-8')
        
        
        try:
            smtpObj = smtplib.SMTP_SSL(config.config.get("smtp_host"),config.config.get("smtp_port"))
            smtpObj.login(config.config.get("smtp_username"),config.config.get("smtp_password"))
            smtpObj.sendmail(sender, receivers, message.as_string())
            smtpObj.quit()
        except smtplib.SMTPException as e:
            print(e)
            return self.error(ErrorCode.EMAIL_SEND_FAILED)
        
        return self.success()
    
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
        if User.expand_objects.filter(tenant=tenant,username=username).count():
            return False, ErrorCode.USERNAME_EXISTS_ERROR
        
        return True, None

    def check_email_exists(self, email, tenant):
        """检查邮箱是否已存在

        Args:
            email (str): 邮箱
            tenant (Tenant): 租户

        Returns:
            (bool,ErrorCode): email是否存在以及对应错误
        """
        if not email:
            return False, ErrorCode.EMAIL_EMPTY

        if User.expand_objects.filter(tenant=tenant,email=email).count():
            return False, ErrorCode.EMAIL_EXISTS_ERROR
        return True, None
    
    @operation(UpdateMineEmailOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def update_mine_email(self, request, tenant_id: str,data:UpdateMineEmailIn):
        """ 普通用户：更新手机号码
        """
        email = data.email
        ret, message = self.check_email_exists(email, request.tenant)
        if not ret:
            return self.error(message)
        
        if not check_email_code(email,data.code):
            return self.error(ErrorCode.EMAIL_CODE_MISMATCH)
        
        user = request.user
        user.email=data.email
        user.save()
        
        return self.success()
    
    @operation(MineEmailOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def mine_email(self,request,tenant_id: str):
        user = request.user
        user_expand = User.expand_objects.filter(id=user.id).first()
        
        config = self.get_tenant_configs(request.tenant).first()
        
        if not config:
            return self.error(
                ErrorCode.CONFIG_IS_NOT_EXISTS
            )
        
        return self.success(
            data={
                "current_email": user_expand.get("email",None),
                "email": "",
                "code": "",
                "config_id": config.id.hex,
            },
        )
    
extension = EmailAuthFactorExtension()
