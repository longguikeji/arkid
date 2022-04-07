import uuid
import json
import logging
from .constants import KEY
from arkid import core
from arkid.core import extension, event 
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
    
class TranslationZhExtension(extension.Extension):
    def load(self):
        super().load()
        
        self.register_languge(
            'zh-hans',
            {"data":"数据"}
        )
    

extension = TranslationZhExtension(
    package="com.longgui.translation_zh",
    description="""国际化插件：
    中文（zh_Hans）
    """,
    version='1.0',
    labels='translation',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)

