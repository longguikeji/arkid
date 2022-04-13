from ninja import Schema, ModelSchema
from arkid.core.api import api
from typing import Union
from typing_extensions import Annotated
from pydantic import Field
from arkid.core.extension import ExtensionConfigSchema

class ExtensionConfigSchemaIn(Schema):
    config_uuid: str
    ext_uuid: str
    config: ExtensionConfigSchema

class ExtensionConfigSchemaOut(Schema):
    config_uuid: str
    ext_uuid: str
    ext_name: str
    ext_icon: str
    config: ExtensionConfigSchema

@api.post("/extension/config", response=ExtensionConfigSchemaOut)
def create_extension_config(request, data: ExtensionConfigSchemaIn):
    # extension.save()
    # return {"uuid": extension.uuid.hex}
    return data


# @api.get("/extensions/{extension_uuid}", response=ExtensionDetailOut)
# def get_extension(request, extension_uuid: str):
#     extension = get_object_or_404(Extension, uuid=extension_uuid, user=request.user)
#     return extension


# @api.get("/extensions", response=List[ExtensionOut])
# def list_extensions(request, status: str = None):
#     if not status:
#         qs = Extension.active_objects.filter(user=request.user)
#     else:
#         qs = Extension.active_objects.filter(user=request.user, status=status)
#     return qs


# @operation(roles=["tenant-user", "platform-user"])
# def update_extension(request, extension_uuid: str, payload: ExtensionIn):
#     extension = get_object_or_404(Extension, uuid=extension_uuid, user=request.user)
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


# @api.delete("/extensions/{extension_uuid}")
# def delete_extension(request, extension_uuid: str):
#     extension = get_object_or_404(Extension, uuid=extension_uuid)
#     extension.delete()
#     return {"success": True}