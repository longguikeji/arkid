import base64
from io import BytesIO
import os
import random
import string
import uuid
from arkid.core import actions, pages
from arkid.core.api import operation
from arkid.core.extension.auth_factor import AuthFactorExtension, BaseAuthFactorSchema
from arkid.common.logger import logger
from pydantic import Field
from typing import List, Optional
from arkid.core.extension import create_extension_schema
from arkid.core.models import Tenant
from .schema import *
from django.db import transaction
from arkid.core.translation import gettext_default as _
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.core.cache import cache
from .error import ErrorCode

class AuthCodeAuthFactorExtension(AuthFactorExtension):
    """图形验证码认证因素插件
    """
    def load(self):
        """加载插件
        """
        self.create_extension_config_schema()
        self.create_extension_settings_schema()
        self.register_extension_api()
        super().load()
    
    def authenticate(self, event, **kwargs):
        pass

    @transaction.atomic()
    def register(self, event, **kwargs):
        pass

    def reset_password(self, event, **kwargs):
        pass
    
    def create_login_page(self, event, config, config_data):
        pass
    
    def fix_login_page(self, event,**kwargs):
        # 生成验证码
        items = [
            {
                "type": "text",
                "name": "authcode",
                "append":{
                    "type": "image",
                    "http": {
                        "url": self.generate_code_path,
                        "method": "get",
                    },
                },
                "http":{
                    "url": self.check_code_path,
                    "method": "post",
                    "params": {
                        "authcode_key": "",
                        "authcode": ""
                    }
                }
            },
            {
                "type": "hidden",
                "name": "authcode_key",
            },
        ]
        for login_pages,ext in event.data["login_pages"]:
            for config_id,login_page in login_pages.items():
                if config_id == uuid.UUID(event.data["main_auth_factor_id"]).hex:
                    for form in login_page[self.LOGIN]["forms"]:
                        form["items"].extend(items)

    def create_register_page(self, event, config, config_data):
        pass

    def create_password_page(self, event, config, config_data):
        pass

    def create_other_page(self, event, config, config_data):
        """创建其他页面（本插件无相关页面）

        Args:
        
            event (Event): 事件
            config (TenantExtensionConfig): 插件运行时配置
        """
        pass
    
    def create_auth_manage_page(self):
        return super().create_auth_manage_page()
    
    def create_extension_config_schema(self):
        """创建插件运行时配置schema描述
        """
        AuthCodeAuthFactorSchema = create_extension_schema(
            'AuthCodeAuthFactorSchema',
            __file__,
            [
                (
                    'login_enabled', 
                    bool, 
                    Field(
                        default=False, 
                        title=_('login_enabled', '启用登录'),
                        # read_only=True
                    )
                ),
                (
                    'register_enabled', 
                    bool, 
                    Field(
                        default=False, 
                        title=_('register_enabled', '启用注册'),
                        # read_only=True
                    )
                ),
                (
                    'reset_password_enabled', 
                    bool, 
                    Field(
                        default=False, 
                        title=_('reset_password_enabled', '启用重置密码'),
                        # read_only=True
                    )
                ),
            ],
            BaseAuthFactorSchema,
        )
        self.register_auth_factor_schema(AuthCodeAuthFactorSchema, 'authcode')
    
    def create_extension_settings_schema(self):
        AuthCodeAuthFactorSettingsSchema = create_extension_schema(
            'AuthCodeAuthFactorSettingsSchema',
            __file__,
            [
                ('width', int, Field(title=_("验证码图片宽度"),default=180)),
                ('height',  int, Field(title=_("验证码图片高度"),default=60)),
                ('auth_code_length',  int, Field(title=_("验证码长度"),default=4)),
            ]
        )

        self.register_settings_schema(AuthCodeAuthFactorSettingsSchema)
    
    def get_random_char(self,auth_code_length=4):
        '''
        获取随机字符组合
        '''
        chr_all = string.ascii_letters + string.digits
        str_random = ''.join(random.sample(chr_all, auth_code_length))
        return str_random

    def get_random_color(self, low, high):
        '''
        获取随机颜色
        '''
        return (
            random.randint(low, high),
            random.randint(low, high),
            random.randint(low, high),
        )

    def get_authcode_picture(self,auth_code_length=4,width=180,height=60):
        '''
        制作验证码图片
        '''
        # 创建空白画布
        image = Image.new('RGB', (width, height), self.get_random_color(20, 100))
        # 验证码的字体
        font = ImageFont.truetype(
            os.path.join(
                os.path.dirname(
                    os.path.abspath(
                        __file__
                    )
                ),
                'assets/stxinwei.ttf'
            ),
            40
        )
        # 创建画笔
        draw = ImageDraw.Draw(image)
        # 获取验证码
        char_4 = self.get_random_char(auth_code_length)
        # 向画布上填写验证码
        for i in range(auth_code_length):
            draw.text(
                (40 * i + 10, 0),
                char_4[i],
                font=font,
                fill=self.get_random_color(100, 200),
            )
        # 绘制干扰点
        for x in range(random.randint(200, 600)):
            x = random.randint(1, width - 1)
            y = random.randint(1, height - 1)
            draw.point((x, y), fill=self.get_random_color(50, 150))
        # 模糊处理
        image = image.filter(ImageFilter.BLUR)
        key = self.generate_key()
        buf = BytesIO()
        # 将图片保存在内存中，文件类型为png
        image.save(buf, 'png')
        byte_data = buf.getvalue()
        base64_str = base64.b64encode(byte_data)
        return key, char_4, base64_str
    
    def generate_key(self):
        key = '{}'.format(uuid.uuid4().hex)
        return key

    @operation(GenrateAuthCodeOut)
    def get_authcode(self, request, tenant_id: str):
        tenant = Tenant.active_objects.get(id=tenant_id)
        settings = self.get_settings(tenant)
        key, code, image = self.get_authcode_picture(
            settings.settings.get("auth_code_length",4),
            settings.settings.get("width",180),
            settings.settings.get("height",60)
        )
        
        cache.set(key,code)
        return {
            "data": {
                "image": str(image, 'utf8'),
                "authcode_key": key
            }
        }
    
    @operation(CheckAuthCodeOut)
    def check_auth_code(self,request,tenant_id:str,data:CheckAuthCodeIn):
        
        if cache.get(data.authcode_key) == data.authcode:
            return self.success()
        else:
            return self.error(
                ErrorCode.AUTHCODE_NOT_MATCH
            )
    
    def register_extension_api(self):
        self.generate_code_path = self.register_api(
            '/auth_code/',
            'GET',
            self.get_authcode,
            tenant_path=True,
            auth=None,
            response=GenrateAuthCodeOut,
        )
        
        self.check_code_path = self.register_api(
            '/auth_code/',
            'POST',
            self.check_auth_code,
            tenant_path=True,
            auth=None,
            response=CheckAuthCodeOut,
        )

extension = AuthCodeAuthFactorExtension()
