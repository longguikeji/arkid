import uuid
import json
import logging
from .constants import KEY
from arkid import core
from arkid.core import extension, event 
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
    
class InternationalEnUsExtension(extension.Extension):
    def load(self):
        super().load()
        
        self.register_languge(
            'zh-hans',
            _("Simplified Chinese"),
            os.path.join(settings.BASE_DIR,'extension_root/com_longgui_international_en_us/locale')
        )
    

extension = InternationalEnUsExtension(
    package="com.longgui.international_en_us",
    description="""国际化插件：
    英语（en-US）
    """,
    version='1.0',
    labels='international',
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)

