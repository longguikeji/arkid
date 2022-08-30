
from api.v1.schema.message import *
from arkid.core.constants import *
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.models import Message
from arkid.core.api import GlobalAuth, api,operation
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
    items = Message.active_objects.filter(user__tenant__id=tenant_id)
    
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
    item = get_object_or_404(Message.active_objects,id=id)
    item.delete()
    return ErrorDict(ErrorCode.OK)