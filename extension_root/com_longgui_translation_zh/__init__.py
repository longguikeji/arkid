import uuid
import json
import logging
from .constants import KEY
from arkid import core
from arkid.core import extension, event
from arkid.core.extension.language import LanguageExtension
from arkid.core.translation import gettext_default as _
from django.conf import settings
import os
    
class TranslationZhExtension(LanguageExtension):
    def load(self):
        super().load()
        
        self.load_language_data(
            {"data":"数据"},
            _('简体中文')
        )
    

extension = TranslationZhExtension(
    package="com.longgui.translation_zh",
    name='中文语言包',
    version='1.0',
    labels='translation',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)

