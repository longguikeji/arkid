from uuid import UUID
from django import dispatch
from django.db.models import F
from ninja import Schema
from pydantic import Field
from typing import List
from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.extension.front_theme import FrontThemeExtension
from arkid.core.event import dispatch_event, Event, CREATE_FRONT_THEME_CONFIG
from arkid.extension.utils import import_extension

FrontThemeListSchemaItem = FrontThemeExtension.create_composite_config_schema(
    'FrontThemeListSchemaItem',
)
class FrontThemeListSchemaOut(Schema):
    data: List[FrontThemeListSchemaItem]
    
@api.get("/tenant/{tenant_id}/front_theme/", response=FrontThemeListSchemaOut, tags=["前端主题"],auth=None)
def get_front_theme_list(request, tenant_id: str):
    """ 前端主题配置列表"""
    extensions = Extension.active_objects.filter(type=FrontThemeExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions).annotate(package=F('extension__package'))
    return {"data": list(configs.values('package','id','name','type','config'))}

FrontThemeConfigGetOut = FrontThemeExtension.create_composite_config_schema('FrontThemeConfigGetOut')
class GetFrontThemeOut(Schema):
    data: FrontThemeConfigGetOut

@api.get("/tenant/{tenant_id}/front_theme/{id}/", response=GetFrontThemeOut, tags=["前端主题"],auth=None)
def get_front_theme(request, tenant_id: str, id: str):
    """ 获取前端主题配置,TODO """
    config = TenantExtensionConfig.active_objects.get(id=id)
    return {"data":config}

CreateFrontThemeIn = FrontThemeExtension.create_composite_config_schema(
    'CreateFrontThemeIn',
    exclude=['id']
)
class CreateFrontThemeOut(Schema):
    config_id: str

@api.post("/tenant/{tenant_id}/front_theme/", response=CreateFrontThemeOut, tags=["前端主题"],auth=None)
def create_front_theme(request, tenant_id: str, data:CreateFrontThemeIn):
    """ 创建前端主题配置,TODO """
    extension = Extension.active_objects.filter(package = data.package).first()
    if extension:
        ext = import_extension(extension.ext_dir)
        tenant = request.tenant
        config = ext.create_tenant_config(tenant, data.config.dict(), data.name, data.type)
        return {'config_id':config.id.hex}
    return {'error':'无法找到{data.package}对应的插件'}

@api.put("/tenant/{tenant_id}/front_theme/{id}/", tags=["前端主题"],auth=None)
def update_front_theme(request, tenant_id: str, id: str):
    """ 编辑前端主题配置,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/front_theme/{id}/", tags=["前端主题"],auth=None)
def delete_front_theme(request, tenant_id: str, id: str):
    """ 删除前端主题配置,TODO
    """
    return {}


