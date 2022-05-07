
from django.shortcuts import render
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from django.views import View
from django.urls import re_path
from django.http.response import FileResponse

class FrontThemeExtension(Extension):
    
    TYPE = "front_theme"
    
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig
    
    @property
    def type(self):
        return FrontThemeExtension.TYPE

    def load(self):
        self.listen_event()
        super().load()

    def register_front_theme(self, type, schema, css_file):
        self.register_config_schema(schema, self.package + '_' + type)
        self.register_composite_config_schema(schema, type, exclude=['extension'])
        class CSSView(View):
            def get():
                return FileResponse(open(css_file, 'rb'))
                
        css_urls = [
            re_path(
                rf'^front_theme/{self.name}/{type}/css/',
                CSSView.as_view(),
                name=f'{self.name}_{type}_css',
            ),
        ]
        self.register_routers(css_urls, True)
    
    def create_front_theme_config(self, event,  **kwargs):
        # 保存
        pass
        


class BaseFrontThemeConfigSchema(Schema):
    priority: int = Field(default=1, title=_('Priority', '优先级'))
    css_url: str = Field(title=_('CSS URL','样式地址'))