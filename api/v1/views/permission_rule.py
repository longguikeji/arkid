from ninja.pagination import paginate
from arkid.core.api import api, operation
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.translation import gettext_default as _
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.extension.impower_rule import ImpowerRuleBaseExtension
from arkid.extension.models import Extension, TenantExtensionConfig
from arkid.core.pagenation import CustomPagination
from api.v1.schema.permission_rule import *


@api.get("/tenant/{tenant_id}/permission_rules/", tags=["授权规则"], response=List[PermissionRuleListItemOut], auth=None)
@operation(PermissionRuleListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_permission_rules(request, tenant_id: str):
    """ 授权规则列表
    """
    extensions = Extension.active_objects.filter(type=ImpowerRuleBaseExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(tenant__id=tenant_id, extension__in=extensions).all()
    return [
        {
            "id": config.id.hex,
            "type": config.type,
            "name": config.name,
            "extension_name": config.extension.name,
            "extension_package": config.extension.package,
        } for config in configs
    ]

@api.get(operation_id="",path="/tenant/{tenant_id}/permission_rules/{id}/", response=PermissionRuleOut, tags=["授权规则"], auth=None)
@operation(PermissionRuleOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_permission_rule(request, tenant_id: str, id: str):
    """ 获取授权规则
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

@api.post("/tenant/{tenant_id}/permission_rules/", response=PermissionRuleCreateOut, tags=["授权规则"], auth=None)
@operation(PermissionRuleCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_permission_rule(request, tenant_id: str, data: PermissionRuleCreateIn):
    """ 创建授权规则
    """
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.name = data.dict()["name"]
    config.type = data.type
    config.save()
    return ErrorDict(ErrorCode.OK)

@api.post("/tenant/{tenant_id}/permission_rules/{id}/", response=PermissionRuleUpdateOut, tags=["授权规则"],auth=None)
@operation(PermissionRuleUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_permission_rule(request, tenant_id: str, id: str, data: PermissionRuleUpdateIn):
    """ 编辑授权规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id,
        id=id
    )
    for attr, value in data.dict().items():
        setattr(config, attr, value)
    config.save()
    return ErrorDict(ErrorCode.OK)

@api.delete("/tenant/{tenant_id}/permission_rules/{id}/", response=PermissionRuleDeleteOut, tags=["授权规则"],auth=None)
@operation(PermissionRuleDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_permission_rule(request, tenant_id: str, id: str):
    """ 删除授权规则
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id
    )
    config.delete()
    return ErrorDict(ErrorCode.OK)


