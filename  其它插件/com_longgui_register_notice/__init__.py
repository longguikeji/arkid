import json
from ninja import Field, Query
from typing import List, Optional
from arkid.core import api as core_api, event as core_event
from arkid.core.extension import create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.core.api import operation
from arkid.core.constants import *
from arkid.core.extension import Extension
from arkid.core import actions
from io import BytesIO
from .schema import *

RegisterNoticeConfigSchema = create_extension_schema(
    'RegisterNoticeConfigSchema',
    __file__,
    base_schema=RegisterNoticeConfigSchema
)

class RegisterNoticeExtension(Extension):

    TYPE = "register_notice"

    @property
    def type(self):
        return RegisterNoticeExtension.TYPE

    def load(self):
        self.register_settings_schema(RegisterNoticeConfigSchema)
        super().load()
        self.listen_event(core_event.CREATE_LOGIN_PAGE_RULES, self.register_privacy)

    def register_privacy(self, event, **kwargs):
        """
        获取隐私协议
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            dict: 协议内容
        """
        data = event.data
        from arkid.extension.models import TenantExtension
        tenant = event.tenant
        extension = self.model
        te = TenantExtension.valid_objects.filter(
            tenant_id=tenant.id,
            extension_id=extension.id,
        ).first()
        if te:
            title = te.settings.get('caption', '')
            content = te.settings.get('content', '')
            if title and content:
                for value, info in data:
                    value_dicts = value.values()
                    for value_dict in value_dicts:
                        register_dict = value_dict.get('register', None)
                        if register_dict:
                            forms_dicts = register_dict.get('forms', [])
                            for forms_dict in forms_dicts:
                                items = forms_dict.get('items', [])
                                items.append({
                                    'name': 'privacy',
                                    'type': 'checkbox',
                                    'placeholder': title,
                                    'content': content,
                                })
        
extension = RegisterNoticeExtension()