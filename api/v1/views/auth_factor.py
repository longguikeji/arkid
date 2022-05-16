from distutils.command.build_ext import extension_name_re
from distutils.command.config import config
from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.error import ErrorCode
from api.v1.schema.auth_factor import AuthFactorCreateIn, AuthFactorCreateOut, AuthFactorDeleteOut, AuthFactorListOut, AuthFactorOut, AuthFactorUpdateIn, AuthFactorUpdateOut


@api.get("/tenant/{tenant_id}/auth_factors/", response=AuthFactorListOut, tags=[_("认证因素")], auth=None)
@operation(AuthFactorListOut)
def get_auth_factors(request, tenant_id: str):
    """ 认证因素列表
    """
    extensions = Extension.active_objects.filter(
        type=AuthFactorExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(
        tenant__id=tenant_id, extension__in=extensions).all()
    return {
        "data": [
            {
                "id": config.id.hex,
                "type": config.type,
                "name": config.name,
                "extension_name": config.extension.name,
                "extension_package": config.extension.package,
            } for config in configs
        ]
    }


@api.get("/tenant/{tenant_id}/auth_factors/{id}/", response=AuthFactorOut, tags=["认证因素"], auth=None)
@operation(AuthFactorOut)
def get_auth_factor(request, tenant_id: str, id: str):
    """ 获取认证因素
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id,
        id=id
    )
    return {
        "data": {
            "id": config.id.hex,
            "type": config.type,
            "package": config.extension.package,
            "name":config.name,
            "config":config.config
        }
    }

@api.post("/tenant/{tenant_id}/auth_factors/", response=AuthFactorCreateOut, tags=["认证因素"], auth=None)
@operation(AuthFactorCreateOut)
def create_auth_factor(request, tenant_id: str, data: AuthFactorCreateIn):
    """ 创建认证因素
    """
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.name = data.dict()["name"]
    config.type = data.type
    config.save()
    return {"data":{"config_id": config.id.hex}}

@api.post("/tenant/{tenant_id}/auth_factors/{id}/", response=AuthFactorUpdateOut, tags=["认证因素"], auth=None)
@operation(AuthFactorUpdateOut)
def update_auth_factor(request, tenant_id: str, id: str, data: AuthFactorUpdateIn):
    """ 编辑认证因素
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    config.update(**(data.dict()))
    return {"data":{"config_id": config.id.hex}}


@api.delete("/tenant/{tenant_id}/auth_factors/{id}/", response=AuthFactorDeleteOut, tags=["认证因素"], auth=None)
@operation(AuthFactorDeleteOut)
def delete_auth_factor(request, tenant_id: str, id: str):
    """ 删除认证因素
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id
    )
    config.delete()
    return {"data":{'error': ErrorCode.OK.value}}
