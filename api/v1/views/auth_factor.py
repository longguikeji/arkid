from ninja import Schema
from typing import Union, Literal, List, Optional
from pydantic import Field
from arkid.core import extension
from arkid.core.api import api
from django.db import transaction
from arkid.core.schema import RootSchema
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension

AuthFatorSchemaIn = AuthFactorExtension.create_composite_config_schema(
    'AuthFatorSchemaIn',
    id=(Optional[str] , Field()),
    test=str,
)

class AuthFatorSchemaOut(Schema):
    config_id: str

@transaction.atomic
@api.post("/tenant/{tenant_id}/auth_factors/", response=AuthFatorSchemaOut, tags=['认证因素'], auth=None)
def create_auth_factor(request, tenant_id: str, data: AuthFatorSchemaIn):
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.save()
    return {"config_id": config.id.hex}


AuthFatorListSchemaItem = AuthFactorExtension.create_composite_config_schema(
    'AuthFatorListSchemaItem',
)


@api.get("/tenant/{tenant_id}/auth_factors/", response=List[AuthFatorListSchemaItem], tags=['认证因素'], auth=None)
def get_auth_factor_list(request, tenant_id: str):
    extensions = Extension.active_objects.filter(type=AuthFactorExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(extension__in=extensions).all()
    return configs

@api.get("/tenant/{tenant_id}/auth_factors/{id}/", tags=["认证因素"],auth=None)
def get_auth_factor(request, tenant_id: str, id: str):
    """ 获取认证因素,TODO
    """
    return {}


@api.put("/tenant/{tenant_id}/auth_factors/{id}/", tags=["认证因素"],auth=None)
def update_auth_factor(request, tenant_id: str, id: str):
    """ 编辑认证因素,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/auth_factors/{id}/", tags=["认证因素"],auth=None)
def delete_auth_factor(request, tenant_id: str, id: str):
    """ 删除认证因素,TODO
    """
    return {}
