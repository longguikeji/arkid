import base64
from io import BytesIO
import json
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
from arkid.core import event as core_event

class AuthCodeAuthFactorExtension(AuthFactorExtension):
    """图形验证码认证因素插件
    """
    def load(self):
        """加载插件
        """
        self.create_extension_config_schema()
        self.create_extension_settings_schema()
        self.register_extension_api()
        self.listen_event(core_event.AUTHRULE_FIX_LOGIN_PAGE,self.fix_login_page)
        self.listen_event(core_event.AUTHRULE_CHECK_AUTH_DATA,self.check_auth_data)
        
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
    
    def fix_login_page(self, event, **kwargs):
        """向login_pages填入认证元素

        Args:
            event: 事件
        """
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

    def check_auth_data(self, event, **kwargs):
        """ 响应检查认证凭证事件

        Args:
            event: 事件
        """
        tenant = event.tenant
        request = event.request
        
        data = request.POST or json.load(request.body)
        
        authcode = data.get('authcode')
        authcode_key = data.get('authcode_key')
        
        if not self.check_authcode(authcode,authcode_key):
            return False,self.error(
                ErrorCode.AUTHCODE_NOT_MATCH
            )
        return True,None
            
    def create_register_page(self, event, config, config_data):
        pass

    def create_password_page(self, event, config, config_data):
        pass

    def create_other_page(self, event, config, config_data):
        pass
    
    def create_auth_manage_page(self):
        pass
    
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
        """创建租户配置schama
        """
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
    
    def get_random_char(self,auth_code_length=4)->str:
        """获取随机字符组合

        Args:
            auth_code_length (int, optional): 图形验证码长度. Defaults to 4.

        Returns:
            str: 随机字符串
        """
        chr_all = string.ascii_letters + string.digits
        str_random = ''.join(random.sample(chr_all, auth_code_length))
        return str_random

    def get_random_color(self, low, high):
        """获取随机颜色

        Args:
            low (int): 下限
            high (int): 上限

        Returns:
            tuple(int,int,int): RGB
        """
        return (
            random.randint(low, high),
            random.randint(low, high),
            random.randint(low, high),
        )

    def get_authcode_picture(self,auth_code_length=4,width=180,height=60):
        """制作验证码图片

        Args:
            auth_code_length (int, optional): 验证码长度. Defaults to 4.
            width (int, optional): 图形宽度. Defaults to 180.
            height (int, optional): 图形高度. Defaults to 60.

        Returns:
            tuple(str,str,image): 缓存key,图形验证码,图片
        """
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
        """生成随机key

        Returns:
            str: 随机key
        """
        key = '{}'.format(uuid.uuid4().hex)
        return key

    @operation(GenrateAuthCodeOut)
    def get_authcode(self, request, tenant_id: str):
        """视图：获取图形验证码

        Args:
            request (HttpRequest): 请求
            tenant_id (str): 租户ID

        Returns:
            HttpResponse: 图片与key
        """
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
        """视图：校验图形验证码

        Args:
            request (HttpRequest): 请求
            tenant_id (str): 租户ID
            data (CheckAuthCodeIn): 待校验数据

        Returns:
            HttpResponse: 校验结果
        """
        if self.check_authcode(data.authcode, data.authcode_key):
            return self.success()
        else:
            return self.error(
                ErrorCode.AUTHCODE_NOT_MATCH
            )
            
    def check_authcode(self,authcode,authcode_key):
        """校验图形验证码

        Args:
            authcode (str): 图形验证码
            authcode_key (str): 图形验证码缓存KEY

        Returns:
            bool: 验证结果
        """
        return cache.get(authcode_key).lower() == authcode.lower()
    
    def register_extension_api(self):
        """注册插件API
        """
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
