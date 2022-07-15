from distutils.command.build_ext import extension_name_re
from distutils.command.config import config
from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.api import api, operation
from ninja.pagination import paginate
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_rule import AuthRuleExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.error import ErrorCode, ErrorDict
from api.v1.schema.auth_rule import AuthRuleCreateIn, AuthRuleCreateOut, AuthRuleDeleteOut, AuthRuleListItemOut, AuthRuleListOut, AuthRuleOut, AuthRuleUpdateIn, AuthRuleUpdateOut
from arkid.core.pagenation import CustomPagination


@api.get("/tenant/{tenant_id}/auth_rules/", response=List[AuthRuleListItemOut], tags=[_("认证规则")])
@operation(List[AuthRuleListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_auth_rules(request, tenant_id: str):
    """ 认证规则列表
    """
    extensions = Extension.active_objects.filter(
        type=AuthRuleExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(
        tenant__id=tenant_id, extension__in=extensions).all()
    return [
        {
            "id": config.id.hex,
            "type": config.type,
            "name": config.name,
            "extension_name": config.extension.name,
            "extension_package": config.extension.package,
        } for config in configs
    ]


@api.get("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleOut, tags=["认证规则"])
@operation(AuthRuleOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
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
            "name": config.name,
            "config": config.config
        }
    }


@api.post("/tenant/{tenant_id}/auth_rules/", response=AuthRuleCreateOut, tags=["认证规则"])
@operation(AuthRuleCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
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
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleUpdateOut, tags=["认证规则"])
@operation(AuthRuleUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_auth_rule(request, tenant_id: str, id: str, data: AuthRuleUpdateIn):
    """ 编辑认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id,
        id=id
    )
    for attr, value in data.dict().items():
        setattr(config, attr, value)
    config.save()
    return ErrorDict(ErrorCode.OK)


@api.delete("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleDeleteOut, tags=["认证规则"])
@operation(AuthRuleDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_auth_rule(request, tenant_id: str, id: str):
    """ 删除认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id
    )
    config.delete()
    return ErrorDict(ErrorCode.OK)
