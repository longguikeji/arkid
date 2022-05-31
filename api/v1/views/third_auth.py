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
from django.db.models import F

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
    configs = TenantExtensionConfig.valid_objects.annotate(extension_package=F('extension__package'),extension_name=F('extension__name')).select_related("extension").filter(
        tenant_id=tenant_id, extension__type=ExternalIdpExtension.TYPE
    )

    return configs

@api.get(
    "/tenant/{tenant_id}/third_auths/{id}/",
    tags=["第三方认证"],
    auth=None,
    response=ThirdAuthOut,
)
@operation(ThirdAuthOut)
def get_third_auth(request, tenant_id: str, id: str):
    """获取第三方认证"""
    config = TenantExtensionConfig.valid_objects.annotate(package=F('extension__package')).select_related("extension").get(id=id)
    return {
        "data": config
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
    extension_config = extension.create_tenant_config(
        request.tenant, data.config.dict(), data.dict()["name"], data.type
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
    config = TenantExtensionConfig.valid_objects.get(id=id)
    config.config = data.config.dict()
    config.save()
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

    config = TenantExtensionConfig.valid_objects.get(id=id)
    config.delete()
    return {'error': ErrorCode.OK.value}
