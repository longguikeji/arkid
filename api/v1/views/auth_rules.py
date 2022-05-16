from distutils.command.build_ext import extension_name_re
from distutils.command.config import config
from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_rule import AuthRuleExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.error import ErrorCode
from api.v1.schema.auth_rule import AuthRuleCreateIn, AuthRuleCreateOut, AuthRuleDeleteOut, AuthRuleListOut, AuthRuleOut, AuthRuleUpdateIn, AuthRuleUpdateOut


@api.get("/tenant/{tenant_id}/auth_rules/", response=AuthRuleListOut, tags=[_("认证规则")], auth=None)
@operation(AuthRuleListOut)
def get_auth_rules(request, tenant_id: str):
    """ 认证规则列表
    """
    extensions = Extension.active_objects.filter(
        type=AuthRuleExtension.TYPE).all()
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


@api.get("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleOut, tags=["认证规则"], auth=None)
@operation(AuthRuleOut)
def get_auth_rule(request, tenant_id: str, id: str):
    """ 获取认证规则
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

@api.post("/tenant/{tenant_id}/auth_rules/", response=AuthRuleCreateOut, tags=["认证规则"], auth=None)
@operation(AuthRuleCreateOut)
def create_auth_rule(request, tenant_id: str, data: AuthRuleCreateIn):
    """ 创建认证规则
    """
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.name = data.dict()["name"]
    config.type = data.type
    config.save()
    return {"data":{"config_id": config.id.hex}}

@api.put("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleUpdateOut, tags=["认证规则"], auth=None)
@operation(AuthRuleUpdateOut)
def update_auth_rule(request, tenant_id: str, id: str, data: AuthRuleUpdateIn):
    """ 编辑认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    config.update(**(data.dict()))
    return {"data":{"config_id": config.id.hex}}


@api.delete("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleDeleteOut, tags=["认证规则"], auth=None)
@operation(AuthRuleDeleteOut)
def delete_auth_rule(request, tenant_id: str, id: str):
    """ 删除认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    config.delete()
    return {"data":{'error': ErrorCode.OK.value}}
