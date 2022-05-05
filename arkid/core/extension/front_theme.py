
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig

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
        super().load()

    def register_front_theme_schema(self, schema, type):
        self.register_config_schema(schema, self.package + '_' + type)
        self.register_composite_config_schema(schema, type, exclude=['extension'])
    
    def register_front_theme(self, type, name, css_url):
        pass


class BaseFrontThemeSchema(Schema):
    priority: int = Field(default=1, title=_('Priority', '优先级'))
    css_url: str = Field(title=_('CSS URL','样式地址'))