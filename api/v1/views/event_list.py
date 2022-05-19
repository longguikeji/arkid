from typing import List
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core import event
from ninja import Schema
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination

class GetEventListOutItem(Schema):
    tag:str
    name:str
    description:str

@api.get("/tenant/{tenant_id}/event_list/", response=List[GetEventListOutItem], tags=["事件列表"],auth=None)
@operation(List[GetEventListOutItem])
@paginate(CustomPagination)
def get_event_list(request, tenant_id: str):
    """ 事件列表 """
    events = []
    for event_type in event.tag_map_event_type.values():
        events.append({
            'tag':event_type.tag,
            'name':event_type.name,
            'description':event_type.description
        })
    return events