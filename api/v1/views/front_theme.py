from ninja import Schema
from typing import List
from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.extension.front_theme import FrontThemeExtension

FrontThemeListSchemaItem = FrontThemeExtension.create_composite_config_schema(
    'FrontThemeListSchemaItem',
)
class FrontThemeListSchemaOut(Schema):
    data: List[FrontThemeListSchemaItem]
    
@api.get("/tenant/{tenant_id}/front_theme/", response=FrontThemeListSchemaOut, tags=["前端主题"],auth=None)
def get_front_theme_list(request, tenant_id: str):
    """ 前端主题配置列表"""
    extensions = Extension.active_objects.filter(type=FrontThemeExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions)
    return {"data": configs}

FrontThemeConfigDetailOut = FrontThemeExtension.create_composite_config_schema('FrontThemeConfigDetailOut')
class FrontThemeDetailOut(Schema):
    data: FrontThemeConfigDetailOut

@api.get("/tenant/{tenant_id}/front_theme/{id}/", response=FrontThemeConfigDetailOut, tags=["前端主题"],auth=None)
def get_front_theme(request, tenant_id: str, id: str):
    """ 获取前端主题配置,TODO """
    config = TenantExtensionConfig.active_objects.get(id=id)
    return {"data":config}

@api.post("/tenant/{tenant_id}/front_theme/", tags=["前端主题"],auth=None)
def create_front_theme(request, tenant_id: str):
    """ 创建前端主题配置,TODO
    """
    return {}

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


