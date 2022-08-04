from types import SimpleNamespace
from uuid import UUID
from django import dispatch
from django.db.models import F
from ninja import Schema
from pydantic import Field
from typing import List
from arkid.core.pagenation import CustomPagination
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.schema import ResponseSchema, RootSchema
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.extension.front_theme import FrontThemeExtension
from arkid.core.event import dispatch_event, Event, CREATE_FRONT_THEME_CONFIG
from arkid.extension.utils import import_extension
from ninja.pagination import paginate
class FrontThemeListSchemaItem(Schema):
    id:str = Field()
    name:str = Field(title=_('配置名'))
    package:str = Field(title=_('插件包名'))
    type:str = Field(title=_('主题类型'))
    css_url:str = Field(title=_('CSS文件地址'))
    priority:int = Field(title=_('优先级'))

class FrontThemeListOut(ResponseSchema):
    data: List[FrontThemeListSchemaItem]
    
@api.get("/tenant/{tenant_id}/front_theme/", response=List[FrontThemeListSchemaItem], tags=["前端主题"], auth=None)
@operation(FrontThemeListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_front_theme_list(request, tenant_id: str):
    """ 前端主题配置列表 """
    extensions = Extension.active_objects.filter(type=FrontThemeExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions).annotate(package=F('extension__package')).values('package','id','name','type','config')
    datas = []
    for config in configs:
        data = {
            'id' : config['id'].hex,
            'package' : config['package'],
            'name' : config['name'],
            'type' : config['type'],
            'priority' : config['config']['priority'],
            'css_url' : config['config']['css_url'],
        }
        datas.append(data)
    return datas

@api.get("/tenant/{tenant_id}/load_front_theme/", response=List[FrontThemeListSchemaItem], tags=["前端主题"], auth=None)
def load_front_theme_list(request, tenant_id: str):
    """ 前端主题配置列表 """
    extensions = Extension.active_objects.filter(type=FrontThemeExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions).annotate(package=F('extension__package')).values('package','id','name','type','config')
    datas = []
    for config in configs:
        data = {
            'id' : config['id'].hex,
            'package' : config['package'],
            'name' : config['name'],
            'type' : config['type'],
            'priority' : config['config']['priority'],
            'css_url' : config['config']['css_url'],
        }
        datas.append(data)
    return datas

GetFrontThemeOut = FrontThemeExtension.create_composite_config_schema('GetFrontThemeOut')

@api.get("/tenant/{tenant_id}/front_theme/{id}/", response=GetFrontThemeOut, tags=["前端主题"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_front_theme(request, tenant_id: str, id: str):
    """ 获取前端主题配置 """
    config = TenantExtensionConfig.active_objects.filter(id=id).annotate(package=F('extension__package')).values('package','id','name','type','config').first()
    return config

CreateFrontThemeIn = FrontThemeExtension.create_composite_config_schema(
    'CreateFrontThemeIn',
    exclude=['id']
)
class CreateFrontThemeOut(Schema):
    config_id: str

@api.post("/tenant/{tenant_id}/front_theme/", response=CreateFrontThemeOut, tags=["前端主题"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_front_theme(request, tenant_id: str, data:CreateFrontThemeIn):
    """ 创建前端主题配置 """
    extension = Extension.active_objects.filter(package = data.package).first()
    if extension:
        ext = import_extension(extension.ext_dir)
        tenant = request.tenant
        data = SimpleNamespace(**data.dict())
        config = ext.create_tenant_config(tenant, data.config, data.name, data.type)
        return {'config_id':config.id.hex}
    return {'error':'无法找到{data.package}对应的插件'}


@api.post("/tenant/{tenant_id}/front_theme/{id}/", response=CreateFrontThemeOut, tags=["前端主题"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_front_theme(request, tenant_id: str, id: str, data: CreateFrontThemeIn):
    """ 编辑前端主题配置,TODO """
    extension = Extension.active_objects.filter(package = data.package).first()
    if extension:
        ext = import_extension(extension.ext_dir)
        data = SimpleNamespace(**data.dict())
        ext.update_tenant_config(id, data.config, data.name, data.type)
        return {'config_id': id}
    return {'error':'无法找到{data.package}对应的插件'}


@api.delete("/tenant/{tenant_id}/front_theme/{id}/", tags=["前端主题"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_front_theme(request, tenant_id: str, id: str):
    """ 删除前端主题配置,TODO """
    config = TenantExtensionConfig.objects.get(id=id)
    config.delete()
    return {'config_id': id}


