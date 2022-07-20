from typing import List
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from arkid.core import event
from ninja import Field, Schema
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.config import get_app_config

class GetEventListOutItem(Schema):
    tag:str = Field(title=_("标签"))
    name:str = Field(title=_("名称"))
    description:str = Field(title=_("描述"))
    url:str = Field(title=_("文档链接"))

@api.get("/tenant/{tenant_id}/event_list/", response=List[GetEventListOutItem], tags=["事件列表"])
@operation(List[GetEventListOutItem], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_event_list(request, tenant_id: str):
    """ 事件列表 """
    events = []
    host = get_app_config().get_host()
    for event_type in event.tag_map_event_type.values():
        events.append({
            'tag':event_type.tag,
            'name':event_type.name,
            'description':event_type.description,
            'url': f'{host}/arkid/%20%20%20用户指南/用户手册/%20租户管理员/扩展能力/事件列表/#{event_type.name}'
        })
    return events