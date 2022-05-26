from ninja import Schema, ModelSchema
from arkid.core import extension
from arkid.core.api import api
from typing import List, Union
from typing_extensions import Annotated
from pydantic import Field
from arkid.core.extension import Extension
from arkid.extension.utils import import_extension
from arkid.extension.models import TenantExtensionConfig, Extension as ExtensionModel
from arkid.core.error import ErrorCode


ExtensionConfigSchemaIn = Extension.create_config_schema(
    'ExtensionConfigSchemaIn',
    extension_id=str,
)

class ExtensionConfigSchemaOut(Schema):
    config_id: str


@api.post("/extensions/{extension_id}/unload/",  tags=['平台插件'], auth=None)
def unload_extension(request, extension_id: str):
    """卸载插件
    """
    extension = ExtensionModel.objects.filter(id=extension_id).first()
    if extension:
        ext = import_extension(extension.ext_dir)
        ext.unload()
        return {'extension_id': ext.model.id.hex}
    else:
        return {}


@api.post("/extensions/{extension_id}/load/", tags=['平台插件'], auth=None)
def load_extension(request, extension_id: str):
    """加载插件
    """
    extension = ExtensionModel.objects.filter(id=extension_id).first()
    if extension:
        ext = import_extension(extension.ext_dir)
        ext.start()
        return {'extension_id': ext.model.id.hex}
    else:
        return {}

ExtensionProfileGetSchemaOut = Extension.create_profile_schema('ExtensionProfileGetSchemaOut')

@api.post("/extensions/{extension_id}/profile/", response=ExtensionProfileGetSchemaOut, tags=['平台插件'], auth=None)
def get_extension_profile(request, extension_id: str):
    """获取插件启动配置
    """
    extension = ExtensionModel.objects.filter(id=extension_id).first()
    return extension

class ExtensionListOut(ModelSchema):
    
    class Config:
        model= ExtensionModel
        model_fields=["id","name","type","package","labels","version","is_active","is_allow_use_platform_config"]

@api.get("/extensions/", response=List[ExtensionListOut], tags=['平台插件'], auth=None)
def list_extensions(request, status: str = None):
    """ 获取平台插件列表 TODO
    """
    if not status:
        qs = ExtensionModel.active_objects.all()
    else:
        qs = ExtensionModel.active_objects.filter(status=status).all()
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


@api.delete("/extensions/{id}/",tags=['平台插件'])
def delete_extension(request, id: str):
    """ 删除平台插件 TODO
    """
    return {"success": True}

@api.post("/extensions/{id}/",tags=['平台插件'])
def update_extension(request, id: str):
    """ 更新平台插件 TODO
    """
    return {"success": True}

@api.get("/extensions/{id}/",tags=['平台插件'])
def get_extension(request, id: str):
    """ 获取平台插件信息 TODO
    """
    return {"success": True}

@api.post("/extensions/{id}/active/", tags=["租户插件"],auth=None)
def toggle_extension_status(request, id: str):
    """ 租户插件列表
    """
    extension= ExtensionModel.objects.get(id=id)
    ext = import_extension(extension.ext_dir)
    if extension.is_active:
        ext.unload()
        extension.is_active = False
    else:
        ext.load()
        extension.is_active = True

    extension.save()
    return {'error': ErrorCode.OK.value}