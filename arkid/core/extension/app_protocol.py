from ninja import Schema
from pydantic import Field
from typing import Optional
from abc import abstractmethod
from typing import Union, Literal
from ninja.orm import create_schema
from arkid.core.extension import Extension
from arkid.extension.models import TenantExtensionConfig
from arkid.core.translation import gettext_default as _
from arkid.core.models import App
from arkid.core import api as core_api, event as core_event

app_protocol_schema_map = {}

def create_app_protocol_extension_config_schema(schema_cls, **field_definitions):
    """创建应用协议类插件配置的Schema
    
    schema_cls只接受一个空定义的Schema
    Examples:
        >>> from ninja import Schema
        >>> from pydantic import Field
        >>> class ExampleExtensionConfigSchema(Schema):
        >>>     pass
        >>> create_app_protocol_extension_config_schema(
        >>>     ExampleExtensionConfigSchema, 
        >>>     field_name=( field_type, Field(...) )
        >>> )

    Args:
        schema_cls (ninja.Schema): 需要创建的Schema class
        field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
    """
    for schema in app_protocol_schema_map.values():
        core_api.add_fields(schema, **field_definitions)
    core_api.add_fields(schema_cls, data=(Union[tuple(app_protocol_schema_map.values())], Field(discriminator='app_type'))) # type: ignore


class AppProtocolExtension(Extension):

    app_type_map = []

    def load(self):
        super().load()

        self.listen_event(core_event.CREATE_APP, self.filter_event_handler)
        self.listen_event(core_event.UPDATE_APP, self.filter_event_handler)
        self.listen_event(core_event.DELETE_APP, self.filter_event_handler)
    

    def register_config_schema(self, schema, app_type, package=None,**kwargs):
        # 父类
        super().register_config_schema(schema, package, **kwargs)

        # app_type = kwargs.get('app_type', None)
        # if app_type is None:
        #     raise Exception('')
        new_schema = create_schema(App,
            name=self.package+'_config', 
            exclude=['is_del', 'is_active', 'updated', 'created', 'tenant', 'secret', 'type'],
            custom_fields=[
                ("app_type", Literal[app_type], Field()),
                ("config", schema, Field())
            ],
        )
        app_protocol_schema_map[app_type] = new_schema
        self.app_type_map.append(app_type)
        #
    
    def filter_event_handler(self, event, **kwargs):
        if event.data.app_type in self.app_type_map:
            data = event.data
            if event.tag == core_event.CREATE_APP:
                return self.create_app(event, data.config)
            elif event.tag == core_event.UPDATE_APP:
                return self.update_app(event, data.config)
            elif event.tag == core_event.DELETE_APP:
                return self.delete_app(event, data.config)
        return False

    
    @abstractmethod
    def create_app(self, event, config):
        pass

    @abstractmethod
    def update_app(self, event, config):
        pass

    @abstractmethod
    def delete_app(self, event, config):
        pass
    
