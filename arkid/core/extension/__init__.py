from abc import ABC, abstractmethod
from typing import Union, Literal
from typing_extensions import Annotated
from pydantic import Field
from django.urls import include, re_path
from pathlib import Path
from arkid import config
from types import SimpleNamespace
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.core import management
from arkid.core import api as core_api, pages as core_page, routers as core_routers, event as core_event
from arkid.core import urls as core_urls, expand as core_expand, models as core_models, translation as core_translation
from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel
from ninja import Schema
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja.orm import create_schema



app_config = config.get_app_config()

Event = core_event.Event
EventType = core_event.EventType


def create_extension_config_schema(schema_cls, **field_definitions):
    """创建插件配置的Schema
    
    schema_cls只接受一个空定义的Schema
    Examples:
        >>> from ninja import Schema
        >>> from pydantic import Field
        >>> class ExampleExtensionConfigSchema(Schema):
        >>>     pass
        >>> create_extension_config_schema(
        >>>     ExampleExtensionConfigSchema, 
        >>>     field_name=( field_type, Field(...) )
        >>> )

    Args:
        schema_cls (ninja.Schema): 需要创建的Schema class
        field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
    """
    for schema in config_schema_map.values():
        core_api.add_fields(schema, **field_definitions)
    core_api.add_fields(schema_cls, __root__=(Union[tuple(config_schema_map.values())], Field(discriminator='package'))) # type: ignore

config_schema_map = {}

class Extension(ABC):
    """插件基类
    """

    def __init__(self, package, version, description, labels, homepage, logo, author) -> None:
        self.package = package
        self.version = version
        self.description = description
        self.labels = labels
        self.homepage = homepage
        self.logo = logo
        self.author = author
        self.name = self.package.replace('.', '_')
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        # self.config_schema_map = 
        self.lang_code = None


    @property
    def ext_dir(self):
        return self._ext_dir

    @ext_dir.setter
    def ext_dir(self, value: str):
        self._ext_dir = value

    @property
    def full_name(self):
        return str(self.ext_dir).replace('/','.')

    def migrate_extension(self) -> None:
        extension_migrate_foldname = Path(self.ext_dir) / 'migrations'
        if not extension_migrate_foldname.exists():
            return
        settings.INSTALLED_APPS += (self.full_name, )
        apps.app_configs = OrderedDict()
        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)

        # management.call_command('makemigrations', self.name, interactive=False)
        print(f'Migrate {self.name}')
        management.call_command('migrate', self.name, interactive=False)

    def register_routers(self, urls_ext, tenant_urls=False):
        if tenant_urls:
            urls_ext = [re_path(r'tenant/(?P<tenant_id>[\w-]+)/', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)
        else:
            urls_ext = [re_path('', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)

    def register_extend_field(self, model_cls, model_field, alias=None):
        if issubclass(model_cls, core_expand.TenantExpandAbstract):
            table = core_models.Tenant._meta.db_table
        elif issubclass(model_cls, core_expand.UserExpandAbstract):
            table = core_models.User._meta.db_table
        elif issubclass(model_cls, core_expand.UserGroupExpandAbstract):
            table = core_models.UserGroup._meta.db_table
        elif issubclass(model_cls, core_expand.AppExpandAbstract):
            table = core_models.App._meta.db_table
        elif issubclass(model_cls, core_expand.AppGroupExpandAbstract):
            table = core_models.AppGroup._meta.db_table
        elif issubclass(model_cls, core_expand.PermissionExpandAbstract):
            table = core_models.Permission._meta.db_table
        elif issubclass(model_cls, core_expand.ApproveExpandAbstract):
            table = core_models.Approve._meta.db_table
        elif issubclass(model_cls, core_expand.TenantConfigExpandAbstract):
            table = core_models.TenantConfig._meta.db_table
        else:
            raise Exception('非法的扩展字段类对应的父类')

        data = SimpleNamespace(
            table = table,
            field = alias or model_field,
            extension = self.name,
            extension_model_cls = model_cls,
            extension_table = model_cls._meta.db_table,
            extension_field = model_field,
        )

        self.extend_fields.append(data)
        core_expand.field_expand_map.append(data)

    def listen_event(self, tag, func):
        def signal_func(event, **kwargs2):
            # 判断租户是否启用该插件
            # tenant
            # 插件名 tag
            # func.__module__ 'extension_root.abc.xx'
            # kwargs2.pop()
            # Extension.
            return func(event=event, **kwargs2)

        core_event.listen_event(tag, signal_func, listener=self)
        self.events.extend((tag, signal_func))        

    def register_event(self, tag, name, data_model=None, description=''):
        tag = self.package + '_' + tag
        core_event.register_event(tag, name, data_model, description)
        self.event_tags.append(tag)
        return tag

    def dispatch_event(self, event):
        return core_event.dispatch_event(event=event, sender=self)

    def register_extend_api(self, api_schema_cls, **field_definitions):
        core_api.add_fields(api_schema_cls, **field_definitions)
        self.extend_apis.append((api_schema_cls, field_definitions.keys()))
        
    def register_languge(self, lang_code:str = 'en', lang_maps={}):
        self.lang_code = lang_code
        if lang_code in core_translation.extension_lang_maps.keys():
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        else:
            core_translation.extension_lang_maps[lang_code] = {}
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        core_translation.lang_maps = core_translation.reset_lang_maps()
        
    def register_front_routers(self, router, primary=''):
        """
        primary: 一级路由名字，由 core_routers 文件提供定义
        """
        router.path = self.package
        router.change_page_tag(self.package)

        for old_router, old_primary in self.front_routers:
            if old_primary == primary:
                self.front_routers.remove((old_router, old_primary))
                core_routers.unregister_front_routers(old_router, old_primary)

        core_routers.register_front_routers(router, primary)
        self.front_routers.append((router, primary))

    def register_front_pages(self, page):
        page.tag = self.package + '_' + page.tag

        core_page.register_front_pages(page)
        self.front_pages.append(page)

    def register_config_schema(self, schema, package=None, **kwargs):
        # class XxSchema(Schema):
        #     config: schema
            # package: Literal[package or self.package] # type: ignore
        new_schema = create_schema(TenantExtensionConfig,
            name=self.package+'_config', 
            fields=['id'],
            custom_fields=[
                ("package", Literal[package or self.package], Field()),  # type: ignore
                ("config", schema, Field())
            ],
        )
        config_schema_map[package or self.package] = new_schema


        
    def get_tenant_configs(self, tenant):
        ext = ExtensionModel.objects.filter(package=self.package, version=self.version).first()
        configs = TenantExtensionConfig.objects.filter(tenant=tenant, extension=ext).all()
        return configs

    def get_config_by_id(self, id):
        return TenantExtensionConfig.objects.get(id=id)
    
    def update_tenant_config(self, id,  config):
        return TenantExtensionConfig.objects.get(id=id).update(config=config)

    def create_tenant_config(self, tenant, config):
        ext = ExtensionModel.objects.filter(package=self.package, version=self.version).first()
        return TenantExtensionConfig.objects.create(tenant=tenant, extension=ext, config=config)

    def load(self):
        self.migrate_extension()
        # self.install_requirements() sys.modeles

    def unload(self):
        core_urls.unregister(self.urls)
        for tag, func in self.events:
            core_event.unlisten_event(tag, func)
        for field in self.extend_fields:
            core_expand.field_expand_map.remove(field)
        for api_schema_cls, fields in self.extend_apis:
            core_api.remove_fields(api_schema_cls, fields)
        for old_router, old_primary in self.front_routers:
            core_routers.unregister_front_routers(old_router, old_primary)
        for page in self.front_pages:
            core_page.unregister_front_pages(page)
        for tag in self.event_tags:
            core_event.unregister_event(tag)

        if self.lang_code:
            core_translation.extension_lang_maps[self.lang_code].pop(self.name)
            if not core_translation.extension_lang_maps[self.lang_code]:
                core_translation.extension_lang_maps.pop(self.lang_code)
            core_translation.lang_maps = core_translation.reset_lang_maps()
