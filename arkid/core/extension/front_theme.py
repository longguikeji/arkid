
from django.shortcuts import render
from ninja import Schema
from typing import List, Optional, Literal
from pydantic import Field
from abc import abstractmethod
from arkid.config import get_app_config
from arkid.core.extension import Extension, create_extension_schema_by_package
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig
from django.views import View
from django.urls import re_path, reverse
from django.http.response import FileResponse
from arkid.core.event import CREATE_FRONT_THEME_CONFIG

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
        # self.listen_event(CREATE_FRONT_THEME_CONFIG, self.create_front_theme_config)
        super().load()

    def register_front_theme_by_file(self, type, css_file):
        class CSSView(View):
            def get():
                return FileResponse(open(css_file, 'rb'))
                
        css_urls = [
            re_path(
                rf'^front_theme/{self.pname}/{type}/css/',
                CSSView.as_view(),
                name=f'{type}',
            ),
        ]
        self.register_routers(css_urls, False)
        
        host = get_app_config().get_frontend_host()
        css_url = host+reverse('{self.name}:{type}')
        self.register_front_theme(type, css_url)
        
    def register_front_theme(self, type, css_url):
        
        schema = create_extension_schema_by_package(
            'MateriaConfigSchema',
            self.package, 
            base_schema = BaseFrontThemeConfigSchema,
            fields=[
                ('css_url', Literal[css_url], Field(title=_('CSS URL','样式地址'))),
            ]
        )
        self.register_config_schema(schema, self.package + '_' + type)
        self.register_composite_config_schema(schema, type, exclude=['extension'])
        
        


class BaseFrontThemeConfigSchema(Schema):
    priority: int = Field(default=1, title=_('Priority', '优先级'))
    # css_url: str = Field(title=_('CSS URL','样式地址'))