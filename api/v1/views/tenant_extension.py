from uuid import UUID
from datetime import datetime
from ninja import Query, Schema, ModelSchema
from arkid.core.api import api, operation
from typing import List,Optional
from pydantic import Field
from arkid.core.extension import Extension
from arkid.core.models import Tenant
from arkid.extension.models import TenantExtensionConfig, TenantExtension, Extension as ExtensionModel
from arkid.core.translation import gettext_default as _
from arkid.core.pagenation import CustomPagination
from ninja.pagination import paginate
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.constants import TENANT_ADMIN, PLATFORM_ADMIN
from arkid.core.schema import ResponseSchema
from django.conf import settings
from arkid.common.arkstore import (
    get_arkstore_access_token,
    get_arkstore_extensions_rented,
    check_time_and_user_valid
)


ExtensionConfigSchemaIn = Extension.create_config_schema(
    'ExtensionConfigSchemaIn',
    exclude=[
        "id",
        "extension_id"
    ]
)


ExtensionConfigGetSchemaOut = Extension.create_config_schema(
    'ExtensionConfigGetSchemaOut',
    id=(UUID, Field(hidden=True, read_only=True))
)

class ExtensionConfigGetOut(ResponseSchema):
    data:ExtensionConfigGetSchemaOut

class ExtensionConfigCreateSchemaOut(Schema):
    config_id: str


class TenantExtensionConfigOut(ModelSchema):
    
    class Config:
        model= TenantExtensionConfig
        model_fields=["id","name","type"]


@api.post("/tenant/{tenant_id}/extension/{extension_id}/config/", response=ExtensionConfigCreateSchemaOut,  tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_extension_config(request, tenant_id: str, extension_id: str, data: ExtensionConfigSchemaIn):
    '''租户下，创建插件运行时配置'''
    settings, created = TenantExtension.objects.get_or_create(
            tenant_id=tenant_id,
            extension_id=extension_id,
        )
    if not settings.is_rented:
        return {"error": ErrorCode.OK.value, "message": "插件未租赁或租赁已到期"}

    config = TenantExtensionConfig.objects.create(
        name = data.dict()["name"],
        tenant_id=tenant_id,
        extension_id=extension_id,
        config=data.dict()["config"],
    )
    return {"config_id": config.id.hex}


@api.get("/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/", response=ExtensionConfigGetOut, tags=['租户插件'])
@operation(ExtensionConfigGetOut,roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_extension_config(request, tenant_id: str, extension_id: str, config_id: str):
    '''租户下，插件运行时配置列表'''
    config = TenantExtensionConfig.objects.get(
        tenant_id=tenant_id,
        extension_id=extension_id,
        id=config_id,
    )
    config.package = config.extension.package
    return {"data":config}


@api.post("/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/", response=ExtensionConfigGetSchemaOut, tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_extension_config(request, tenant_id: str, extension_id: str, config_id: str, data: ExtensionConfigSchemaIn):
    '''租户下，插件运行时配置列表'''
    settings, created = TenantExtension.objects.get_or_create(
        tenant_id=tenant_id,
        extension_id=extension_id,
    )
    if not settings.is_rented:
        return {"error": ErrorCode.OK.value, "message": "插件未租赁或租赁已到期"}
    
    config = TenantExtensionConfig.objects.get(
        tenant_id=tenant_id,
        extension_id=extension_id,
        id=config_id,
    )
    config.config = data.config.dict()
    config.save()
    config.package = config.extension.package
    return config


@api.get("/tenant/{tenant_id}/extension/{extension_id}/config/", response=List[TenantExtensionConfigOut], tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_extension_config(request, tenant_id: str, extension_id: str):
    '''租户下，插件运行时配置列表'''
    configs = TenantExtensionConfig.active_objects.filter(
        tenant_id=tenant_id,
        extension_id=extension_id,
    )
    return configs


@api.delete("/tenant/{tenant_id}/extension/{extension_id}/config/{config_id}/", response=ResponseSchema, tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_extension_config(request, tenant_id: str, extension_id: str, config_id: str):
    '''租户下，删除插件运行时配置'''
    config = TenantExtensionConfig.objects.get(
        tenant_id=tenant_id,
        extension_id=extension_id,
        id=config_id,
    )
    config.delete()
    return ErrorDict(ErrorCode.OK)


ExtensionSettingsCreateIn = Extension.create_settings_schema(
    'ExtensionSettingsCreateIn')


ExtensionSettingsGetSchemaOut = Extension.create_settings_schema(
    'ExtensionSettingsGetSchemaOut',
    id=(UUID, Field(hidden=True)),
)


class ExtensionSettingsGetSchemaResponse(ResponseSchema):
    data: ExtensionSettingsGetSchemaOut


@api.post("/tenant/{tenant_id}/extension/{extension_id}/settings/", response=ResponseSchema,  tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_extension_settings(request, tenant_id: str, extension_id: str, data: ExtensionSettingsCreateIn):
    '''租户下，创建插件配置'''
    settings, created = TenantExtension.objects.get_or_create(
        tenant_id=tenant_id,
        extension_id=extension_id,
    )
    if not settings.is_rented:
        return {"error": ErrorCode.OK.value, "message": "插件未租赁或租赁已到期"}

    if data.settings:
        settings.settings = data.settings.dict()
        settings.save()
    
    return {"error": ErrorCode.OK.value, "data": {"settings_id": settings.id.hex}}


@api.get("/tenant/{tenant_id}/extension/{extension_id}/settings/", response=ExtensionSettingsGetSchemaResponse, tags=['租户插件'])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_extension_settings(request, tenant_id: str, extension_id: str):
    '''租户下，获取插件配置'''
    tenant_extension,created = TenantExtension.objects.get_or_create(
        tenant_id=tenant_id,
        extension_id=extension_id,
    )
    tenant_extension.package = tenant_extension.extension.package
    return {"data": tenant_extension}


class ExtensionRentRecordOut(Schema):
    order_type: str
    price_type: str
    use_begin_time: datetime
    use_end_time: datetime
    max_users: int


class TenantExtensionListOut(ModelSchema):
    
    class Config:
        model= ExtensionModel
        model_fields=["id","name","type","package","labels","version"]
        
    labels:Optional[List[str]]


class TenantRentedExtensionListOut(TenantExtensionListOut):
    # lease_records: List[ExtensionRentRecordOut] = Field(
    #     default=[], title=_("Rent Records", "租赁记录")
    # )
    lease_state: Optional[str] = Field(title=_('Lease State', '租赁状态'))
    lease_useful_life: Optional[List[str]] = Field(title=_('Lease Useful Life', '有效期'))


@api.get("/tenant/{tenant_id}/platform/extensions/", tags=["租户插件"],response=List[TenantRentedExtensionListOut])
@operation(List[TenantExtensionListOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_platform_extensions(request, tenant_id: str):
    """ 平台插件列表
    """
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    extensions = ExtensionModel.active_objects.all()
    if settings.IS_CENTRAL_ARKID:
        return extensions

    if tenant.is_platform_tenant:
        for ext in extensions:
            ext.lease_useful_life = ["不限天数，不限人数"]
            ext.lease_state = '已租赁'
        return extensions

    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extensions_rented(access_token)
    extensions_rented = {ext['package']: ext for ext in resp['items']}
    for ext in extensions:
        if ext.package in extensions_rented:
            ext.lease_useful_life = extensions_rented[ext.package]['lease_useful_life']
            ext.lease_state = '已租赁'
            lease_records = extensions_rented[ext.package].get('lease_records') or []
            # check_lease_records_expired
            if check_time_and_user_valid(lease_records, tenant):
                tenant_extension, created = TenantExtension.objects.update_or_create(
                    tenant_id=tenant_id,
                    extension=ext,
                    defaults={"is_rented": True}
                )

    return extensions


@api.get("/tenant/{tenant_id}/tenant/extensions/", tags=["租户插件"],response=List[TenantRentedExtensionListOut])
@operation(List[TenantRentedExtensionListOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_tenant_extensions(request, tenant_id: str):
    """ 租户插件列表
    """
    token = request.user.auth_token
    tenant = Tenant.objects.get(id=tenant_id)
    extension_ids = TenantExtension.valid_objects.filter(tenant_id=tenant_id, is_rented=True).values('extension_id')
    extensions = ExtensionModel.active_objects.filter(id__in = extension_ids)
    if settings.IS_CENTRAL_ARKID:
        return extensions

    if tenant.is_platform_tenant:
        for ext in extensions:
            ext.lease_useful_life = ["不限天数，不限人数"]
            ext.lease_state = '已租赁'
        return extensions

    access_token = get_arkstore_access_token(tenant, token)
    resp = get_arkstore_extensions_rented(access_token)
    extensions_rented = {ext['package']: ext for ext in resp['items']}
    for ext in extensions:
        if ext.package in extensions_rented:
            ext.lease_useful_life = extensions_rented[ext.package]['lease_useful_life']
            ext.lease_state = '已租赁'
            lease_records = extensions_rented[ext.package].get('lease_records') or []
            # check_lease_records_expired
            if check_time_and_user_valid(lease_records, tenant):
                tenant_extension, created = TenantExtension.objects.update_or_create(
                    tenant_id=tenant_id,
                    extension=ext,
                    defaults={"is_rented": True}
                )

    return extensions


@api.post("/tenant/{tenant_id}/tenant/extensions/{id}/active/", tags=["租户插件"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def toggle_tenant_extension_status(request, tenant_id: str, id: str):
    """ 租户插件列表
    """
    extension= TenantExtension.objects.get(id=id)
    extension.is_active = True if extension.is_active is False else False
    extension.save()
    return ErrorDict(ErrorCode.OK)


@api.get("/tenant/{tenant_id}/extensions/{id}/", tags=["租户插件"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_extension(request, tenant_id: str, id: str):
    """ 获取租户插件,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/extensions/{id}/", tags=["租户插件"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_extension(request, tenant_id: str, id: str):
    """ 删除租户插件,TODO
    """
    return {}

class TenantConfigSelectQueryIn(Schema):
    extension__type:Optional[str] =Field(
        title=_("类型")
    )
    
class TenantConfigSelectItemOut(Schema):
    
    id:UUID = Field(
        title=_("ID"),
        hidden=True
    )
    
    name:str = Field(
        title=_("Name")
    )
    
    package:str = Field(
        title=_("插件包名")
    )
class TenantConfigSelectOut(ResponseSchema):
    data:List[TenantConfigSelectItemOut]

@api.get("/tenants/{tenant_id}/config_select/",response=TenantConfigSelectOut, tags=["租户插件"])
@operation(TenantConfigSelectOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_config_select(request,tenant_id: str,query_data:TenantConfigSelectQueryIn=Query(...)):
    """ 分类获取租户下插件配置列表
    """
    tenant = Tenant.active_objects.get(id=tenant_id)
    
    config_list = TenantExtensionConfig.active_objects.filter(
        tenant=tenant,
    )
    query_data = query_data.dict()
    if query_data:
        config_list = config_list.filter(**query_data)
    
    config_list = config_list.all()    
    
    return {
        "data":[{
            "id": item.id,
            "name": item.name,
            "package":item.extension.package
        } for item in config_list]
    }