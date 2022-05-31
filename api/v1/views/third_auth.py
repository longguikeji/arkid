from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.extension.external_idp import ExternalIdpExtension
from arkid.extension.utils import import_extension
from arkid.extension.models import TenantExtensionConfig, Extension, TenantExtension
from uuid import UUID
from django.shortcuts import get_object_or_404
from arkid.core.error import ErrorCode
from ninja import Schema, ModelSchema
from typing import List
from ninja.pagination import paginate
from arkid.core.api import api, operation
from arkid.core.pagenation import CustomPagination
from api.v1.schema.third_auth import (
    ThirdAuthCreateIn,
    ThirdAuthCreateOut,
    ThirdAuthListItemOut,
    ThirdAuthListOut,
    ThirdAuthOut,
    ThirdAuthUpdateIn,
    ThirdAuthUpdateOut,
    ThirdAuthDeleteOut,
)


@api.get(
    "/tenant/{tenant_id}/third_auths/",
    tags=["第三方认证"],
    auth=None,
    response=List[ThirdAuthListItemOut],
)
@operation(ThirdAuthListOut)
@paginate(CustomPagination)
def get_third_auths(request, tenant_id: str):
    """第三方认证列表,TODO"""
    settings = TenantExtension.valid_objects.filter(
        tenant_id=tenant_id, extension__type=ExternalIdpExtension.TYPE
    )
    return [
        {
            "id": setting.id.hex,
            "type": setting.extension.type,
            # "name": setting.name,
            "extension_name": setting.extension.name,
            "extension_package": setting.extension.package,
        }
        for setting in settings
    ]


@api.get(
    "/tenant/{tenant_id}/third_auths/{id}/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthOut,
)
@operation(ThirdAuthOut)
def get_third_auth(request, tenant_id: str, id: str):
    """获取第三方认证"""
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    return {
        "data": {
            "id": setting.id.hex,
            "type": setting.extension.type,
            "package": setting.extension.package,
            # "name": setting.name,
            "config": setting.settings,
        }
    }


@api.post(
    "/tenant/{tenant_id}/third_auths/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthCreateOut,
)
@operation(ThirdAuthCreateOut)
def create_third_auth(request, tenant_id: str, data: ThirdAuthCreateIn):
    """创建第三方认证"""
    extension = Extension.valid_objects.get(package=data.package)
    extension = import_extension(extension.ext_dir)
    extension_setting = extension.update_or_create_settings(
        request.tenant, data.config.dict(), True, False
    )
    return {'error': ErrorCode.OK.value}


@api.put(
    "/tenant/{tenant_id}/third_auths/{id}/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthUpdateOut,
)
def update_third_auth(request, tenant_id: str, id: str, data: ThirdAuthUpdateIn):
    """编辑第三方认证"""
    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    setting.settings = data.config.dict()
    setting.save()
    return {'error': ErrorCode.OK.value}


@api.delete(
    "/tenant/{tenant_id}/third_auths/{id}/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthDeleteOut,
)
@operation(ThirdAuthDeleteOut)
def delete_third_auth(request, tenant_id: str, id: str):
    """删除第三方认证"""

    setting = TenantExtension.valid_objects.get(tenant__id=tenant_id, id=id)
    setting.kill()
    return {'error': ErrorCode.OK.value}
