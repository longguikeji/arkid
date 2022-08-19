
from api.v1.schema.message import *
from arkid.core.constants import *
from arkid.core.error import ErrorCode, ErrorDict
from arkid.core.models import Message
from arkid.core.api import api,operation
from django.shortcuts import get_list_or_404, get_object_or_404
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.extension.models import Extension, TenantExtensionConfig

@api.get("/tenant/{tenant_id}/message/", response=List[MessageListItemOut],tags=["消息管理"])
@operation(MessageListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_messages(request, tenant_id: str):
    """消息列表
    """
    items = Message.expand_objects.filter(tenant__id=tenant_id)
    
    return list(items.all())

@api.post("/tenant/{tenant_id}/message/", response=MessageCreateOut, tags=["消息管理"])
@operation(MessageCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_message(request, tenant_id: str, data: MessageCreateIn):
    """ 创建消息
    """
    item = Message.expand_objects.create(tenant=request.tenant,**data)

    return ErrorDict(ErrorCode.OK)

@api.delete("/tenant/{tenant_id}/message/{id}/", response=MessageDeleteOut, tags=["消息管理"])
@operation(MessageDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_message(request, tenant_id: str, id: str):
    """ 删除消息
    """
    item = get_object_or_404(Message.expand_objects,id=id, is_del=False, is_active=True)
    item.delete()
    return ErrorDict(ErrorCode.OK)

@api.get("/tenant/{tenant_id}/message_extension_config/", response=List[MessageExtesionConfigListItemOut],tags=["消息管理"])
@operation(MessageExtesionConfigListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_message_extension_configs(request, tenant_id: str):
    """消息插件配置列表
    """
    extensions = Extension.active_objects.filter(
        type=MessageExtension.TYPE).all()
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

@api.get("/tenant/{tenant_id}/message_extension_config/{id}/", response=MessageExtesionConfigOut, tags=["消息管理"])
@operation(MessageExtesionConfigOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_message_extension_config(request, tenant_id: str, id: str):
    """ 获取消息插件配置
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


@api.post("/tenant/{tenant_id}/message_extension_config/", response=MessageExtesionConfigCreateOut, tags=["消息管理"])
@operation(MessageExtesionConfigCreateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def create_message_extension_config(request, tenant_id: str, data: MessageExtesionConfigCreateIn):
    """ 创建消息插件配置
    """
    config = TenantExtensionConfig()
    config.tenant = request.tenant
    config.extension = Extension.active_objects.get(package=data.package)
    config.config = data.config.dict()
    config.name = data.dict()["name"]
    config.type = data.type
    config.save()
    
    return ErrorDict(ErrorCode.OK)


@api.post("/tenant/{tenant_id}/message_extension_config/{id}/", response=MessageExtesionConfigUpdateOut, tags=["消息管理"])
@operation(MessageExtesionConfigUpdateOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def update_message_extension_config(request, tenant_id: str, id: str, data: MessageExtesionConfigUpdateIn):
    """ 编辑消息插件配置
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id)
    for attr, value in data.dict().items():
        if attr == "id":
            continue
        setattr(config, attr, value)
    config.save()
    return ErrorDict(ErrorCode.OK)


@api.delete("/tenant/{tenant_id}/message_extension_config/{id}/", response=MessageExtesionConfigDeleteOut, tags=["消息管理"])
@operation(MessageExtesionConfigDeleteOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def delete_message_extension_config(request, tenant_id: str, id: str):
    """ 删除消息插件配置
    """
    config = TenantExtensionConfig.active_objects.get(
        tenant__id=tenant_id, id=id
    )
    config.delete()
    return ErrorDict(ErrorCode.OK)