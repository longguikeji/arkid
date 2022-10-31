from dataclasses import field, fields
from uuid import UUID
from datetime import datetime
from ninja import Schema, ModelSchema
from arkid.core import actions, extension
from arkid.core.api import api, operation
from typing import List, Union,Optional
from typing_extensions import Annotated
from pydantic import Field
from django.conf import settings
from arkid.core.constants import NORMAL_USER, PLATFORM_ADMIN, TENANT_ADMIN
from arkid.core.extension import Extension
from arkid.core.schema import ResponseSchema
from arkid.extension.utils import import_extension, restart_celery
from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from ninja.pagination import paginate
from oauth2_provider.models import Application
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _
from arkid.common.arkstore import get_arkstore_access_token
from .arkstore import get_arkstore_list


ExtensionConfigSchemaIn = Extension.create_config_schema(
    'ExtensionConfigSchemaIn',
    extension_id=str,
)

class ExtensionConfigSchemaOut(Schema):
    config_id: str

ExtensionProfileGetSchemaIn = Extension.create_profile_schema(
    'ExtensionProfileGetSchemaIn',
)

ExtensionProfileGetSchemaOut = Extension.create_profile_schema(
    'ExtensionProfileGetSchemaOut',
    id=(UUID,Field(hidden=True)),
)

class ExtensionProfileGetSchemaResponse(ResponseSchema):
    data: ExtensionProfileGetSchemaOut

@api.get("/extensions/{id}/profile/", response=ExtensionProfileGetSchemaResponse, tags=['平台插件'])
@operation(roles=[PLATFORM_ADMIN])
def get_extension_profile(request, id: str):
    """获取插件启动配置
    """
    extension = ExtensionModel.objects.filter(id=id).first()
    return {"data": extension}

@api.post("/extensions/{id}/profile/", tags=['平台插件'])
@operation(roles=[PLATFORM_ADMIN])
def update_extension_profile(request, id: str, data:ExtensionProfileGetSchemaIn):
    """更新插件启动配置
    """
    extension = ExtensionModel.objects.filter(id=id).first()
    extension.is_active = data.is_active
    extension.is_allow_use_platform_config = data.is_allow_use_platform_config
    if data.profile:
        extension.profile = data.profile.dict()
    extension.save()
    return {'error':ErrorCode.OK.value}

class ExtensionPurchaseRecordOut(Schema):
    order_type: str
    price_type: str
    use_begin_time: datetime
    use_end_time: datetime
    max_users: int

class ExtensionListOut(ModelSchema):
    
    class Config:
        model= ExtensionModel
        model_fields=["id","name","type","package","labels","version","is_active","is_allow_use_platform_config",
            "author", "logo", "homepage"
        ]

    labels:Optional[List[str]]
    is_active: bool = Field(
        title='是否启动',
        item_action={
            "path":"/api/v1/extensions/{id}/toggle/",
            "method":actions.FrontActionMethod.POST.value
        }
    )
    is_allow_use_platform_config: bool = Field(
        title='是否允许租户使用平台配置',
        hidden=True,
        item_action={
            "path":"/api/v1/extensions/{id}/use_platform_config/toggle/",
            "method":actions.FrontActionMethod.POST.value
        }
    )
    # purchase_records: List[ExtensionPurchaseRecordOut] = Field(
    #     default=[], title=_("Purchase Records", "购买记录")
    # )
    purchase_state: Optional[str] = Field(
        title=_('Purchase State', '购买状态')
    )
    purchase_useful_life: Optional[List[str]] = Field(
        title=_('Purchase Useful Life', '有效期')
    )

@api.get("/extensions/", response=List[ExtensionListOut], tags=['平台插件'])
@operation(roles=[PLATFORM_ADMIN])
@paginate(CustomPagination)
def list_extensions(request, status: str = None, category_id: str = None):
    """ 获取平台插件列表"""
    if not status:
        qs = ExtensionModel.valid_objects.filter()
    else:
        qs = ExtensionModel.valid_objects.filter(status=status)

    if category_id and category_id != "" and category_id != "0":
        qs = qs.filter(category_id=int(category_id))

    if settings.IS_CENTRAL_ARKID:
        return qs

    # 如果未绑定中心arkid, 直接返回
    tenant = Tenant.platform_tenant()
    bind = Application.objects.filter(
        uuid = tenant.id,
        name = 'arkid_saas',
    ).exists()
    if not bind:
        return qs

    token = request.user.auth_token
    # access_token = get_arkstore_access_token(tenant, token)
    # resp = get_arkstore_extensions_purchased(access_token)
    resp = get_arkstore_list(request, True, 'extension', all=True)['items']
    extensions_purchased = {ext['package']: ext for ext in resp}
    for ext in qs:
        if ext.package in extensions_purchased:
            ext.purchase_useful_life = extensions_purchased[ext.package].get('purchase_useful_life')
            ext.purchase_state = extensions_purchased[ext.package].get('purchase_state')
    return qs


# @operation(roles=["tenant-user", "platform-user"])
# def update_extension(request, extension_id: str, payload: ExtensionIn):
#     extension = get_object_or_404(Extension, uuid=extension_id, user=request.user)
#     data = payload.dict()
#     file_name = data.pop("file_name")
#     categories = data.pop("categories")
#     price = data.pop("price")
#     price_type = data.pop("price_type")
#     cost_discount = data.pop("cost_discount")

#     labels = data.pop("labels")
#     data["file"] = File.active_objects.filter(name=file_name).first()
#     data["user"] = request.user
#     data["tenant"] = request.user.tenant
#     for attr, value in data.items():
#         setattr(extension, attr, value)
#     if categories:
#         for category in categories:
#             category = Category.active_objects.filter(name=category).first()
#             if category:
#                 extension.categories.add(category)
#     if price:
#         extension.prices.clear()
#         price, is_create = Price.objects.get_or_create(
#             type=price_type,
#             standard_price=price,
#             cost_discount=cost_discount,
#         )
#         extension.prices.add(price)
#     if labels:
#         extension.label = " ".join(labels)
#     extension.save()
#     return {"success": True}


# @api.delete("/extensions/{id}/",tags=['平台插件'])
# def delete_extension(request, id: str):
#     """ 删除平台插件 TODO
#     """
#     return {"success": True}

class ExtensionItemOut(ModelSchema):
    class Config:
        model=ExtensionModel
        model_fields=['id','type']
        
class ExtensionOut(ResponseSchema):
    data:ExtensionItemOut

@api.get("/extensions/{id}/",tags=['平台插件'])
@operation(roles=[PLATFORM_ADMIN])
def get_extension(request, id: str):
    """ 获取平台插件
    """
    instance = ExtensionModel.valid_objects.get(id=id)
    
    return SuccessDict(
        data=instance
    )

class ExtensionMarkDownOut(ResponseSchema):
    data:dict = Field(format='markdown',readonly=True)
    
@api.get("/extensions/{id}/markdown/",tags=['平台插件'], response=ExtensionMarkDownOut)
@operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
def get_extension_markdown(request, id: str):
    """ 获取平台插件的markdown文档"""
    
    ext_model = ExtensionModel.valid_objects.get(id=id)
    import os
    files = os.listdir(ext_model.ext_dir)
    data = {}
    for file in files:
        if file.endswith('.md'):
            md_file = open(ext_model.ext_dir+"/"+file)
            data[file] = md_file.read()
            md_file.close()
    return {"data": data}

@api.post("/extensions/{id}/toggle/", tags=["平台插件"])
@operation(roles=[PLATFORM_ADMIN])
def toggle_extension_active_status(request, id: str):
    """ 切换插件启用状态
    """
    extension= ExtensionModel.objects.get(id=id)
    
    if extension.is_active:
        ext = import_extension(extension.ext_dir)
        ext.stop()
        extension.is_active = False
    else:
        platform_tenant = Tenant.platform_tenant()
        token = request.user.auth_token
        from arkid.common.arkstore import check_arkstore_purcahsed_extension_expired
        if not check_arkstore_purcahsed_extension_expired(platform_tenant, token, extension.package):
            # 插件过期或人数超过限制，请再次购买
            return ErrorDict(ErrorCode.CAN_NOT_ACTIVATE_EXTENSION)

        ext = import_extension(extension.ext_dir)
        ext.start()
        extension.is_active = True

    extension.save()
    restart_celery()
    return ErrorDict(ErrorCode.OK)

@api.post("/extensions/{id}/use_platform_config/toggle/", tags=["平台插件"])
@operation(roles=[PLATFORM_ADMIN])
def toggle_extension_allow_use_platform_config_status(request, id: str):
    """ 切换是否允许租户使用平台配置状态
    """
    extension= ExtensionModel.objects.get(id=id)
    extension.is_allow_use_platform_config = not extension.is_allow_use_platform_config
    extension.save()
    return ErrorDict(ErrorCode.OK)