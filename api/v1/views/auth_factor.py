from ninja import ModelSchema, Schema
from typing import Union, Literal, List, Optional
from pydantic import Field
from arkid.core import extension
from arkid.core.api import api, operation
from django.db import transaction
from arkid.core.schema import RootSchema
from arkid.core.translation import gettext_default as _
from arkid.extension.models import TenantExtensionConfig, Extension
from arkid.core.event import Event, register_event, dispatch_event
from arkid.core.extension.auth_factor import AuthFactorExtension
from arkid.core.error import ErrorCode

AuthFactorSchemaIn = AuthFactorExtension.create_composite_config_schema(
    'AuthFactorSchemaIn',
    exclude=['id']
)

class AuthFactorSchemaOut(Schema):
    config_id: str

@transaction.atomic
@api.post("/tenant/{tenant_id}/auth_factors/", response=AuthFactorSchemaOut, tags=['认证因素'], auth=None)
def create_auth_factor(request, tenant_id: str, data: AuthFactorSchemaIn):
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.name = data.dict()["name"]
    config.type = data.type
    config.save()
    return {"config_id": config.id.hex}


class AuthFactorListOutSchema(ModelSchema):
    
    class Config:
        model=TenantExtensionConfig
        model_fields = ["id","name","type","extension"]

@api.get("/tenant/{tenant_id}/auth_factors/", response=List[AuthFactorListOutSchema], tags=['认证因素'], auth=None)
@operation(List[AuthFactorListOutSchema])
def get_auth_factor_list(request, tenant_id: str):
    """ 获取认证因素列表
    """
    extensions = Extension.active_objects.filter(type=AuthFactorExtension.TYPE).all()
    configs = TenantExtensionConfig.active_objects.filter(tenant=request.tenant, extension__in=extensions).all()
    return configs

AuthFactorOutSchema = AuthFactorExtension.create_composite_config_schema(
    'AuthFactorOutSchema'
)

@api.get("/tenant/{tenant_id}/auth_factors/{id}/",response=AuthFactorOutSchema,tags=["认证因素"],auth=None)
def get_auth_factor(request, tenant_id: str, id: str):
    """ 获取认证因素
    """
    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    return config

AuthFactorUpdateInSchema = AuthFactorExtension.create_composite_config_schema(
    'AuthFactorUpdateInSchema'
)

class AuthFactorUpdateOutSchema(Schema):
    error:bool = Field(
        title=_("状态")
    )

@api.put("/tenant/{tenant_id}/auth_factors/{id}/",response=AuthFactorUpdateOutSchema, tags=["认证因素"],auth=None)
def update_auth_factor(request, tenant_id: str, id: str,data:AuthFactorUpdateInSchema):
    """ 编辑认证因素,TODO
    """
    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    config.update(**(data.dict()))
    return {'error': ErrorCode.OK.value}

class AuthFactorDeleteOutSchema(Schema):
    error:bool = Field(
        title=_("状态")
    )

@api.delete("/tenant/{tenant_id}/auth_factors/{id}/", tags=["认证因素"],auth=None)
def delete_auth_factor(request, tenant_id: str, id: str):
    """ 删除认证因素
    """
    config = TenantExtensionConfig.active_objects.get(tenant__id=tenant_id, id=id)
    config.delete()
    return {'error': ErrorCode.OK.value}