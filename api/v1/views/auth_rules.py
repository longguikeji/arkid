from distutils.command.build_ext import extension_name_re
from distutils.command.config import config
from typing import List
from ninja import Field, ModelSchema, Schema
from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.extension.auth_rule import AuthRuleExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.error import ErrorCode


class AuthRuleListOut(Schema):

    id: str
    type: str = Field(title=_("类型"))
    name: str = Field(title=_("名称"))
    extension_name: str = Field(title=_("插件名称"))
    extension_package: str = Field(title=_("插件包"))


@api.get("/tenant/{tenant_id}/auth_rules/", response=List[AuthRuleListOut], tags=[_("认证规则")], auth=None)
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


AuthRuleOut = AuthRuleExtension.create_composite_config_schema(
    'AuthRuleOut'
)


@api.get("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleOut, tags=["认证规则"], auth=None)
def get_auth_rule(request, tenant_id: str, id: str):
    """ 获取认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    return config


AuthRuleCreateIn = AuthRuleExtension.create_composite_config_schema(
    'AuthRuleCreateIn',
    exclude=['id']
)


class AuthRuleCreateOut(Schema):
    config_id: str


@api.post("/tenant/{tenant_id}/auth_rules/", response=AuthRuleCreateOut, tags=["认证规则"], auth=None)
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
    return {"config_id": config.id.hex}


AuthRuleUpdateIn = AuthRuleExtension.create_composite_config_schema(
    'AuthRuleUpdateIn'
)


class AuthRuleUpdateOut(Schema):
    error: bool = Field(
        title=_("状态")
    )


@api.put("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleUpdateOut, tags=["认证规则"], auth=None)
def update_auth_rule(request, tenant_id: str, id: str, data: AuthRuleUpdateIn):
    """ 编辑认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    config.update(**(data.dict()))
    return config


class AuthRuleDeleteOut(Schema):
    error: bool = Field(
        title=_("状态")
    )


@api.delete("/tenant/{tenant_id}/auth_rules/{id}/", response=AuthRuleDeleteOut, tags=["认证规则"], auth=None)
def delete_auth_rule(request, tenant_id: str, id: str):
    """ 删除认证规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    config.delete()
    return {'error': ErrorCode.OK.value}
