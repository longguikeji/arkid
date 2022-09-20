from typing import Any, List
from arkid.core.schema import ResponseSchema
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.event import Event, dispatch_event, GET_STATISTICS_CHARTS
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN


class ChartsListOut(ResponseSchema):
    data: List[Any]


@api.get("/tenant/{tenant_id}/statistics_charts", tags=['统计图表'], response=ChartsListOut)
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_statistics_charts(request, tenant_id: str):
    '''获取统计图表
    '''
    tenant = request.tenant
    results = dispatch_event(Event(tag=GET_STATISTICS_CHARTS, tenant=tenant, request=request))
    charts = []
    for func, (result, extension) in results:
        if result:
            charts.extend(result)
    return {"data": charts}
