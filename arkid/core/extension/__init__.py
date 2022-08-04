import toml
from abc import ABC, abstractmethod
from enum import Enum
from pyclbr import Function
from typing import Union, Literal, Any, List, Optional, Tuple, Type, Callable
from typing_extensions import Annotated
from uuid import UUID
from pydantic import Field
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from django.urls import include, re_path
from pathlib import Path
from ninja.constants import NOT_SET

from requests import delete
from arkid import config, extension
from types import SimpleNamespace
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.core import management
from arkid.core import api as core_api, pages as core_page, routers as core_routers, event as core_event
from arkid.core import urls as core_urls, expand as core_expand, models as core_models, translation as core_translation
from arkid.core.schema import RootSchema
from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel, TenantExtension
from ninja import Schema
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja.orm import create_schema
from django.db.models import Model
from arkid.common.logger import logger
from arkid.core.models import EmptyModel, Tenant
from functools import partial
from arkid.core.path import API_PATH_HEAD

app_config = config.get_app_config()

Event = core_event.Event
EventType = core_event.EventType


def create_extension_schema(name, file_path, fields: Optional[List[Tuple[str, Any, Any]]] = None, base_schema:Type[Schema] = Schema,  exclude=[]):
    """提供给插件用来创建Schema的方法
    
    注意:
        插件必须使用此方法来定义Schema,避免与其它Schema的命名冲突
    Args:
        name (str): Schema的类名
        file_path (str): 指插件__init__.py文件所在的路径, 用来通过插件的config.toml文件获取package,从而避免schema的命名冲突
        fields (Optional[List[Tuple[str, Any, Any]]], optional): Schema的字段定义
        base_schema (Type[Schema], optional): Schema的基类. 默认为: ninja.Schema
    Returns:
        ninja.Schema : 创建的Schema类
    """
    config_path = Path(file_path).parent / "config.toml"
    if not config_path.exists():
        raise Exception("config.tmol not found")

    config = toml.load(config_path)
    return create_extension_schema_by_package(name, config["package"], fields, base_schema, exclude)


def create_extension_schema_by_package( name, package = '',fields: Optional[List[Tuple[str, Any, Any]]] = None, base_schema:Type[Schema] = Schema,  exclude=[]) :
    """提供给插件用来创建Schema的方法
    
    注意:
        插件必须使用此方法来定义Schema,避免与其它Schema的命名冲突
    Args:
        name (str): Schema的类名
        package (str): 如果是插件调用的该方法,一定要将插件的package传过来,以避免命名冲突
        fields (Optional[List[Tuple[str, Any, Any]]], optional): Schema的字段定义
        base_schema (Type[Schema], optional): Schema的基类. 默认为: ninja.Schema
    Returns:
        ninja.Schema : 创建的Schema类
    """
    if package:
        name = package + '_' + name
    name = name.replace('.','_')
    
    custom_fields = []
    if fields:
        for f_name, f_type, f_field in fields:
            if type(f_type) is Optional:
                continue;
            else:
                f_type = Optional[f_type]
            custom_fields.append((f_name, f_type, f_field))
        
    schema = create_schema(EmptyModel,
            name=name, 
            exclude=['id'],
            custom_fields=custom_fields,
            base_class=base_schema,
        )
    core_api.remove_fields(schema, exclude)
    schema.name = name
    return schema


def create_extension_schema_from_django_model(
        model: Type[Model],
        *,
        name: str = "",
        depth: int = 0,
        fields: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        custom_fields: Optional[List[Tuple[str, Any, Any]]] = None,
        base_class: Type[Schema] = Schema,) :
    """提供给插件通过Django.Model创建Schema的方法
    注意:
        插件必须使用此方法来定义Schema,避免与其它Schema的命名冲突
        
    Args:
        model (Type[Model]): 基于的 Django Model
        name (str, optional): Schema的类名. 
        depth (int, optional): 遍历Django Model的深度. 
        fields (Optional[List[str]], optional): 从Django Model中获取的字段名, 如果是所有的就设为 \_\_all\_\_ . 
        exclude (Optional[List[str]], optional): 从Django Model中排除的字段名. 
        custom_fields (Optional[List[Tuple[str, Any, Any]]], optional): 添加的自定义字段. 
        base_class (Type[Schema], optional): Schema的基类. 
    Returns:
        ninjia.Schema: 新创建的Schema类
    """
    schema = create_schema(model=model, name=name, depth=depth,fields=fields, exclude=exclude, custom_fields=custom_fields, base_class=base_class)
    schema.name = name
    return schema

def create_empty_root_schema(name):
    return create_extension_schema_by_package(name, fields=[("__root__", str, Field())],base_schema=RootSchema,)

def get_root_schema(schema_list, discriminator, depth = 0):
    if len(schema_list) == 0:
        return Schema, Field()
    elif len(schema_list) == 1:
        return list(schema_list)[0],Field()
    else:
        return Union[tuple(schema_list)], Field(discriminator=discriminator, depth=depth)


extension_schema_map = {}
def create_config_schema_from_schema_list(schema_cls_name, schema_list, discriminator, exclude=[], depth = 0, **field_definitions):
    fields = []
    for k,t in field_definitions.items():
        if isinstance(t,tuple):
            t,f = t
        else:
            f = Field()
        fields.append( (k,t,f) )
    
    if len(schema_list) == 0:
        schema = create_extension_schema_by_package(schema_cls_name+'0', exclude=exclude, fields=fields)
    elif len(schema_list) == 1:
        # schema = list(schema_list)[0]
        schema = create_extension_schema_by_package(schema_cls_name+'1', base_schema=list(schema_list)[0], exclude=exclude, fields=fields)
    else:
        new_schema_list = []
        for schema in schema_list:
            schema = create_extension_schema_by_package(schema_cls_name + '_' + schema.name, base_schema=schema)
            core_api.add_fields(schema, **field_definitions)
            core_api.remove_fields(schema, exclude)
            new_schema_list.append(schema)
            
        schema_list = new_schema_list
        root_type, root_field = Union[tuple(schema_list)], Field(discriminator=discriminator, readonly=True, depth=depth)
        
        schema = create_extension_schema_by_package(
            schema_cls_name, 
            fields=[
                ("__root__", root_type, root_field) # type: ignore
            ],
            base_schema=RootSchema,
        )
        extension_schema_map[schema_cls_name] = schema
    return schema

#############################################

def create_extension_page(file_path, page_cls, *args, **kwargs):
    """提供给插件用来创建Page的方法
    
    注意:
        插件必须使用此方法来定义Page,避免与其它page的tag冲突
    Args:
        file_path (str): 指插件__init__.py文件所在的路径, 用来通过插件的config.toml文件获取package,从而避免schema的命名冲突
        page_cls (page): 页面的类，在core.pages中定义的TablePage、TreePage等等
        args (optional): 页面类构造参数
        kwargs (optional): 页面类构造参数
    Returns:
        page : 创建的page_cls的页面实例
    """
    config_path = Path(file_path).parent / "config.toml"
    if not config_path.exists():
        raise Exception("config.tmol not found")

    config = toml.load(config_path)
    page = page_cls(*args, **kwargs)
    page.add_tag_pre(config['package'].replace('.','_'))
    return page


class Extension(ABC):
    """
    Args:
        name (str, ): 插件名字，package中点“.”替换为下划线"_"
    """
    extension_profile_schema_map = {}
    created_extension_profile_schema_list = []
    
    extension_settings_schema_map = {}
    created_extension_settings_schema_list = []
    
    extension_config_schema_map = {}
    created_extension_config_schema_list = []

    @property
    def type(self):
        return 'base'

    def __init__(
        self, 
        package:str = None, 
        version:str = None, 
        name:str = None,  
        logo:str = None, 
        description:str = None, 
        labels:List[str] = None, 
        homepage:str = None, 
        author:str = None
    ):
        """_summary_

        Args:
            package (str): 插件包名，唯一标识
            version (str): 版本号
            name (str): 名称
            logo (str): 插件的图标
            description (str): 描述
            labels (List[str]): 标签
            homepage (str): 主页，URL
            author (str): 作者
        """
        self.package = package
        self.version = version
        self.name = name
        self.description = description
        self._labels = []
        if type(labels) is list:
            self._labels.extend(labels)
        elif labels:
            self._labels.append(labels)
        self.homepage = homepage
        self.logo = logo
        self.author = author
        self.apis = []
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        self.profile_schema_list = []
        self.settings_schema_list = []
        self.config_schema_list = []
        self.lang_code = None

    def load_config(self):
        config_path = Path(self._ext_dir) / "config.toml"
        if config_path.exists():
            config = toml.load(config_path)
            for k, v in config.items():
                setattr(self, k, v)

    @property
    def pname(self):
        return self.package.replace('.', '_')

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value: str):
        if type(value) is list:
            self._labels.extend(value)
        elif value:
            self._labels.append(value)

    @property
    def model(self):
        """插件对应数据库model"""
        extension = ExtensionModel.valid_objects.filter(package=self.package).first()
        if not extension:
            raise Exception(f'cannot find {self.package} in database')
        else:
            return extension

    @property
    def ext_dir(self):
        """插件完整路径，用.分隔"""
        return self._ext_dir

    @ext_dir.setter
    def ext_dir(self, value: str):
        self._ext_dir = value
        self.load_config()

    @property
    def full_name(self):
        """插件完整路径，用/分隔"""
        return str(self.ext_dir).replace('/','.')

    def migrate_extension(self) -> None:
        extension_models = Path(self.ext_dir) / 'migrations'
        if not extension_models.exists():
            return
            
        try:
            print(f'migrate {self.pname} start')
            management.call_command('migrate', self.pname, interactive=False)
            print(f'migrate {self.pname} end')
        except Exception as e:
            print(e)
            print(f'migrate {self.pname} fail')
    
    def create_schema(self, name, fields: Optional[List[Tuple[str, Any, Any]]] = None, base_schema:Type[Schema] = Schema,  exclude=[]):
        return create_extension_schema_by_package(name, self.package, fields, base_schema,  exclude)
            
    def register_api(
        self, 
        path: str,
        method: str,
        view_func: Callable,
        *,
        tenant_path: bool = False,
        auth: Any = NOT_SET,
        response: Any = NOT_SET,
        operation_id: Optional[str] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        deprecated: Optional[bool] = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        url_name: Optional[str] = None,
        include_in_schema: bool = True,):
        """Django-ninja的方式注册自定义API

        Args:
            path (str): 请求路径
            method (str): 请求方法,值为：GET，POST，DELETE，PUT等
            view_func (Callable): api方法
            tenant_path (bool, optional): 是否需要tenant开头，为Ture时，path前自动加上'/tenant/{tenant_id}'的结构. Defaults to False.
            auth (Any, optional): 认证方法. Defaults to NOT_SET.
            response (Any, optional): response schema. Defaults to NOT_SET.
            operation_id (Optional[str], optional):  Defaults to None.
            summary (Optional[str], optional):  Defaults to None.
            description (Optional[str], optional):  Defaults to None.
            tags (Optional[List[str]], optional):  Defaults to None.
            deprecated (Optional[bool], optional):  Defaults to None.
            by_alias (bool, optional):  Defaults to False.
            exclude_unset (bool, optional):  Defaults to False.
            exclude_defaults (bool, optional):  Defaults to False.
            exclude_none (bool, optional):  Defaults to False.
            url_name (Optional[str], optional):  Defaults to None.
            include_in_schema (bool, optional):  Defaults to True.

        Returns:
            str: 真实的地址path
        """
        path = '/' + self.pname + path
        
        if tenant_path:
            path = '/tenant/{tenant_id}' + path
        
        self.apis.append((path, method))
        
        core_api.api.default_router.add_api_operation(
            path,
            [method],
            view_func,
            auth=auth is NOT_SET and core_api.api.auth or auth,
            response=response,
            operation_id=operation_id,
            summary=summary,
            description=description,
            tags=tags or [self.name],
            deprecated=deprecated,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            url_name=url_name,
            include_in_schema=include_in_schema,
        )

        return "/" + API_PATH_HEAD + path
    
    def register_routers(self, urls_ext:List[partial], tenant_urls=False):
        """注册路由

        Args:
            urls_ext (List[partial]): 需要注册的路由
            tenant_urls (bool, optional): 是否要添加 tenant/{tenant_id}/ 前缀. Defaults to False.
        """
        if tenant_urls:
            urls_ext = [re_path(r'tenant/(?P<tenant_id>[\w-]+)/', include((urls_ext, 'extension'), namespace=f'{self.pname}_tenant'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)
        else:
            urls_ext = [re_path('', include((urls_ext, 'extension'), namespace=f'{self.pname}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)

    def register_extend_field(self, 
                              model_cls:Union[
                                  core_models.TenantExpandAbstract,
                                  core_models.UserExpandAbstract,
                                  core_models.UserGroupExpandAbstract,
                                  core_models.AppExpandAbstract,
                                  core_models.AppGroupExpandAbstract,
                                ], model_field:str, alias:str=None):
        """注册扩展数据库字段，对原本数据库字段进行扩展

        Args:
            model_cls (Union[ core_expand.TenantExpandAbstract, core_expand.UserExpandAbstract, core_expand.UserGroupExpandAbstract, core_expand.AppExpandAbstract, core_expand.AppGroupExpandAbstract, ]): 扩展定义的model
            model_field (str): 扩展的字段
            alias (str, optional): 扩展字段在原model中的别名. None意味着就使用model_field作为其在原model中的别名

        Raises:
            Exception: 非法的扩展字段类对应的父类
        """
        data = core_expand.register_expand_field(
            table = model_cls.foreign_key._meta.db_table,
            field = alias or model_field,
            extension_name = self.pname,
            extension_model_cls = model_cls,
            extension_table = model_cls._meta.db_table,
            extension_field = model_field,
        )

        self.extend_fields.append(data)
        

    def listen_event(self, tag:str, func:Function):
        """侦听事件

        Args:
            tag (str): 事件的tag
            func (Function): 回调函数, event, **kwargs为必有参数。其中只有当前插件的package在event.packages中时，该插件才响应该事件。
        """
        def signal_func(event, **kwargs2):
            # 判断租户是否启用该插件
            if not self.model.is_active:
                return
            tenant_extension = TenantExtension.active_objects.filter(is_rented=True, extension=self.model, tenant=event.tenant).first()
            if not event.tenant.is_platform_tenant and not tenant_extension:
                return
            if event.packages and not self.package in event.packages:
                return
            return func(event=event, **kwargs2)

        core_event.listen_event(tag, signal_func, listener=self)
        self.events.append((tag, signal_func))        

    def register_event(self, tag, name, data_schema=None, description=''):
        """注册事件

        Args:
            tag (str): 事件标识
            name (str): 事件名字
            data_schema (schema class, optional): event.data的schema. Defaults to None.
            description (str, optional): 事件描述. Defaults to ''.

        Returns:
            str: 真实事件标识tag，为self.package +'.'+ tag
        """
        tag = self.package + '.' + tag
        core_event.register_event(tag, name, data_schema, description)
        self.event_tags.append(tag)
        return tag
    
    def register_event_type(self, event_type:EventType):
        """注册事件类型

        Args:
            event_type (EventType): 事件类型对象

        Returns:
            EventType: tag = package+'.'+tag
        """
        event_type.tag = self.package + '.' + event_type.tag
        core_event.register_event_type(event_type)
        self.event_tags.append(event_type.tag)
        return event_type

    def dispatch_event(self, event):
        """抛出事件

        Args:
            event (Event): 事件实例

        Returns:
            (tuple[Function, Result]): 事件处理的返回值
        """
        return core_event.dispatch_event(event=event, sender=self)

    def register_extend_api(self, *api_schema_cls, **field_definitions):
        """注册扩展内核API

        Args:
            api_schema_cls (class): API Schema Class
            field_definitions (name=tuple(Type,Field())): 需要增加的字段，example：name=(str, Field(title='名字'))
        """
        for schema_cls in api_schema_cls:
            core_api.add_fields(schema_cls, **field_definitions)
            self.extend_apis.append((schema_cls, list(field_definitions.keys())))

    def register_front_routers(self, router, primary:core_routers.FrontRouter=None):
        """注册前端路由

        Args:
            router (core_routers.FrontRouter): 前端路由实例
            primary (core_routers.FrontRouter, optional): 一级路由名字，由 core_routers 文件提供定义. Defaults to None.
        """
        router.path = self.package.replace('.', '_')
        # router.change_page_tag(self.package.replace('.', '_'))

        for old_router, old_primary in self.front_routers:
            if old_primary == primary:
                self.front_routers.remove((old_router, old_primary))
                core_routers.unregister_front_routers(old_router, old_primary)

        core_routers.register_front_routers(router, primary)
        self.front_routers.append((router, primary))

    def register_front_pages(self, page:core_page.FrontPage):
        """注册前端页面

        Args:
            page (core_pages.FrontPage): 前端页面
        """
        core_page.register_front_pages(page)
        if isinstance(page, tuple) or isinstance(page, list):
            self.front_pages.extend(page)
        else:
            self.front_pages.append(page)

################################################################################
#### Base 
    
    def register_base_schema(self, schema, type, model, fields, schema_map, schema_list, schema_tag=None):
        schema_tag = self.package
        name = schema_tag.replace('.','_')+'_'+type
        new_schema = create_schema(model,
            name = name, 
            fields = fields,
            custom_fields=[
                ("package", Literal[schema_tag], Field()),  # type: ignore
                (type, Optional[schema], Field())
            ],
        )
        new_schema.name = name
        schema_map[schema_tag] = new_schema
        schema_list.append(schema_tag)

    @classmethod
    def create_base_schema(cls, name:str, created_schema_list:list, schema_map, **field_definitions):
        schema = create_empty_root_schema(name)
        cls.refresh_one_created_base_schema(schema, field_definitions, schema_map)
        created_schema_list.append( (schema,field_definitions) )
        return schema
        
    @classmethod
    def refresh_all_created_base_schema(cls, created_schema_list, schema_map):
        for schema,field_definitions in created_schema_list:
            cls.refresh_one_created_base_schema(schema, field_definitions, schema_map)
    
    @classmethod
    def refresh_one_created_base_schema(cls, schema, field_definitions, schema_map):
        temp_schema = create_config_schema_from_schema_list(schema.name+'_temp', schema_map.values(), 'package', **field_definitions)
        core_api.add_fields(schema, __root__=(temp_schema, Field()))

################################################################################

################################################################################
#### Profile 

    def register_profile_schema(self, schema, schema_tag:str=None):
        """注册插件配置 profile schema

        Args:
            schema (class): schema的类
            schema_tag (str, optional): shema的标识, 默认为self.package
        """
        self.register_base_schema(
            schema, 'profile', ExtensionModel, 
            ['id','is_active', 'is_allow_use_platform_config'],
            self.__class__.extension_profile_schema_map,
            self.profile_schema_list, schema_tag
        )

    @classmethod
    def create_profile_schema(cls, name:str, **field_definitions):
        """创建并返回插件配置的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_profile_schema_list, cls.extension_profile_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_profile_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_profile_schema_list, cls.extension_profile_schema_map)
    
################################################################################


################################################################################
#### Settings 

    def register_settings_schema(self, schema, schema_tag=None):
        """注册插件的 租户配置 settings schema

        Args:
            schema (class): schema的类
            schema_tag (str, optional): shema的标识, 默认为self.package
        """
        self.register_base_schema(
            schema, 'settings', TenantExtension, 
            ['id','is_active','use_platform_config'],
            self.__class__.extension_settings_schema_map,
            self.settings_schema_list, schema_tag
        )

    @classmethod
    def create_settings_schema(cls, name:str, **field_definitions):
        """创建并返回插件 租户配置(settings) 的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_settings_schema_list, cls.extension_settings_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_settings_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_settings_schema_list, cls.extension_settings_schema_map)

    def get_settings(self, tenant:Tenant):
        """获取租户配置

        Args:
            tenant (Tenant): 租户

        Returns:
            TenantExtension: 租户配置
        """
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        settings = TenantExtension.valid_objects.filter(tenant=tenant, extension=ext).first()
        return settings

    def update_or_create_settings(self, tenant, settings, is_active, use_platform_config):
        """更新或创建租户配置

        Args:
            tenant (Tenant): 租户
            settings (dict): 租户配置
            is_active (bool): 是否启用
            use_platform_config (bool): 是否使用平台配置

        Returns:
            TenantExtension: 更新或创建的对象
        """
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        tx = TenantExtension.valid_objects.filter(tenant=tenant, extension=ext).first()
        if tx:
            tx.is_active = is_active
            tx.use_platform_config = use_platform_config
            tx.settings = settings
            return tx.save()
            
        return TenantExtension.objects.create(
            tenant=tenant, extension=ext, settings=settings, 
            is_active=is_active, use_platform_config=use_platform_config
        )
    
################################################################################

################################################################################
#### Config 
    
    def register_config_schema(self, schema, schema_tag=None):
        """注册插件的 运行时配置 config schema

        Args:
            schema (class): schema的类
            schema_tag (str, optional): shema的标识, 默认为self.package
        """
        self.register_base_schema(
            schema, 'config', TenantExtensionConfig, 
            ['id','name'],
            self.__class__.extension_config_schema_map,
            self.config_schema_list, schema_tag
        )

    @classmethod
    def create_config_schema(cls, name:str, **field_definitions):
        """创建并返回插件 运行时配置 的Schema
        Args:
            name (str): 需要创建的 Schema Class 的名字
            field_definitions (Any): 任意数量的field,格式为: field_name=(field_type, Field(...))
        """
        return cls.create_base_schema(name, cls.created_extension_config_schema_list, cls.extension_config_schema_map, **field_definitions)
        
    @classmethod
    def refresh_all_created_config_schema(cls):
        cls.refresh_all_created_base_schema(cls.created_extension_config_schema_list, cls.extension_config_schema_map)
        
    def get_tenant_configs(self, tenant):
        """获取当前租户下所有的运行时配置

        Args:
            tenant (Tenant): 租户

        Returns:
            List[TenantExtensionConfig]: tenant下所有的运行时配置
        """
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        configs = TenantExtensionConfig.valid_objects.filter(tenant=tenant, extension=ext).all()
        return configs

    def get_config_by_id(self, id:UUID):
        """通过config_id来获取config

        Args:
            id (UUID): config_id

        Returns:
            TenantExtensionConfig: config
        """
        return TenantExtensionConfig.valid_objects.get(id=id)
    
    def update_tenant_config(self, id,  config, name, type):
        """更新运行时配置

        Args:
            id (str): config_id
            config (dict): config
            name (str): 运行时配置名字
            type (str): 配置类型

        Returns:
            bool: 更新成功True，没有找到该配置返回False
        """
        tenantextensionconfig = TenantExtensionConfig.valid_objects.filter(id=id).first()
        if tenantextensionconfig:
            tenantextensionconfig.name = name
            tenantextensionconfig.type = type

            # 只更新提供的字段，不提供的字段不更新，防止冲掉已经写入的其它字段
            default_config = tenantextensionconfig.config
            config_keys = config.keys()
            for key in config_keys:
                default_config[key] = config.get(key)

            tenantextensionconfig.config = default_config
            tenantextensionconfig.save()
            return True
        else:
            return False 

    def create_tenant_config(self, tenant, config, name, type):
        """创建运行时配置

        Args:
            tenant (Tenant): 租户
            config (dict): config
            name (str): 运行时配置名字
            type (str): 配置类型

        Returns:
            TenantExtensionConfig: 创建的对象
        """
        ext = ExtensionModel.valid_objects.filter(package=self.package).first()
        return TenantExtensionConfig.valid_objects.create(tenant=tenant, extension=ext, config=config, name=name, type=type)
    
    def delete_tenant_config(self, id):
        """删除运行时配置

        Args:
            id (str): config_id

        Returns:
            TenantExtensionConfig: 删除的对象
        """
        return TenantExtensionConfig.objects.delete(id=id)

################################################################################


################################################################################
#### Composite Config 

    def register_composite_config_schema(self, schema, composite_value, exclude=[], package=None):
        """注册复合类型 运行时配置 的Schema

        Args:
            schema (class): Schema类
            composite_value (str): 复合类型
            exclude (list, optional): 从schema的字段中删掉的字段列表. Defaults to [].
            package (str, optional): 自定义package名字，不传就使用self.package， 正常情况不用设置.
        """
        package = package or self.package
        exclude.extend(['is_del', 'is_active', 'updated', 'created', 'tenant'])
        name = package + '_' + composite_value + '_config'
        new_schema = create_schema(self.__class__.composite_model,
            name=name,
            exclude=exclude,
            custom_fields=[
                (self.__class__.composite_key, Literal[composite_value], Field()), # type: ignore
                ("package", Literal[package], Field()), # type: ignore
                ("config", schema, Field()),
            ],
        )
        new_schema.name = name
        if composite_value not in self.__class__.composite_schema_map:
            self.composite_schema_map[composite_value] = {}
        self.composite_schema_map[composite_value][package] = new_schema
    
    @classmethod
    def create_composite_config_schema(cls, schema_cls_name, exclude=[], **field_definitions):
        """创造复合类型 运行时配置 的Schema

        Args:
            schema_cls_name (str): 复合类型运行时配置的Schema的名字
            exclude (list, optional): 去掉的字段列表. Defaults to [].

        Returns:
            Schema: 创建好的Schema
        """
        schema = create_extension_schema_by_package(
            schema_cls_name, 
            fields=[
                ("__root__", str, Field(depth=1)) # type: ignore
            ],
            base_schema=RootSchema,
        )
        cls.created_composite_schema_list.append((schema, field_definitions, exclude))
        cls.refresh_all_created_composite_schema()
        return schema
    
    @classmethod
    def refresh_all_created_composite_schema(cls):
        if not hasattr(cls, "created_composite_schema_list"):
            return
        for created_ext_config_schema, field_definitions, exclude in cls.created_composite_schema_list:
            temp_list = {}
            for composite_key, package_schema_map in cls.composite_schema_map.items():
                schema_name = created_ext_config_schema.name + composite_key
                new_schema = create_config_schema_from_schema_list(
                    schema_name, 
                    package_schema_map.values(),
                    'package',
                    exclude=exclude,
                    **field_definitions,
                )
                temp_list[composite_key] = new_schema
            

            root_type, root_field = get_root_schema(temp_list.values(), cls.composite_key, depth=1)
            core_api.add_fields(created_ext_config_schema, __root__=(root_type, root_field))
            
################################################################################

    def error(self, enum:Enum=None, **kwargs):
        """API接口错误dict

        Args:
            enum (Enum, optional): 错误的枚举类，如果为None，标识成功返回. Defaults to None.

        Returns:
            dict : 生成的错误dict
        """
        if not enum:
            return ErrorDict(ErrorCode.OK, self.package, **kwargs)
        return ErrorDict(enum, self.package, **kwargs)
    
    def success(self, data=None, **kwargs):
        """API接口成功dict

        Args:
            data (dict, optional): 成功时需要返回的数据. Defaults to None.

        Returns:
            dict: 生成的成功dict
        """
        return SuccessDict(data, self.package, **kwargs)

    @abstractmethod
    def load(self):
        """抽象方法，插件加载的入口方法"""
        pass

    def start(self):
        try:
            self.migrate_extension()
        except Exception as e:
            print(e)
            logger.error(e)
        self.load()
        
        if len(self.profile_schema_list) == 0:
            self.register_profile_schema(Optional[dict])
        if len(self.settings_schema_list) == 0:
            self.register_settings_schema(Optional[dict])
        if len(self.config_schema_list) == 0:
            self.register_config_schema(Optional[dict])

        self.__class__.refresh_all_created_profile_schema()
        self.__class__.refresh_all_created_settings_schema()
        self.__class__.refresh_all_created_config_schema()
        self.__class__.refresh_all_created_composite_schema()
        
        # self.install_requirements() sys.modeles

    def unload(self):
        """插件卸载"""
        core_urls.unregister(self.urls)
        for path, method in self.apis:
            path_view = core_api.api.default_router.path_operations[path]
            for operation in path_view.operations:
                if method in operation.methods:
                    path_view.operations.remove(operation)
                    break
        for tag, func in self.events:
            core_event.unlisten_event(tag, func)
        for field in self.extend_fields:
            core_expand.unregister_expand_field(field)
        for api_schema_cls, fields in self.extend_apis:
            core_api.remove_fields(api_schema_cls, fields)
        for old_router, old_primary in self.front_routers:
            core_routers.unregister_front_routers(old_router, old_primary)
        for page in self.front_pages:
            core_page.unregister_front_pages(page)
        for tag in self.event_tags:
            core_event.unregister_event(tag)
        for schema_tag in self.profile_schema_list:
            self.__class__.extension_profile_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_profile_schema()
        for schema_tag in self.settings_schema_list:
            self.__class__.extension_settings_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_settings_schema()
        for schema_tag in self.config_schema_list:
            self.__class__.extension_config_schema_map.pop(schema_tag, None)
        self.__class__.refresh_all_created_config_schema()
        
        delete_ks = []
        if hasattr(self.__class__, 'composite_schema_map'):
            for k,v in self.__class__.composite_schema_map.items():
                v.pop(self.package, None)
                if not self.__class__.composite_schema_map[k]:
                    delete_ks.append(k)
            for k in delete_ks:
                self.__class__.composite_schema_map.pop(k)
            self.__class__.refresh_all_created_composite_schema()

        if self.lang_code:
            core_translation.extension_lang_maps[self.lang_code].pop(self.pname)
            if not core_translation.extension_lang_maps[self.lang_code]:
                core_translation.extension_lang_maps.pop(self.lang_code)
            core_translation.lang_maps = core_translation.reset_lang_maps()
        
        self.apis = []
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        self.profile_schema_list = []
        self.settings_schema_list = []
        self.config_schema_list = []
