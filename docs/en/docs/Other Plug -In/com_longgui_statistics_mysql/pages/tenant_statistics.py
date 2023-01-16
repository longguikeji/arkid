from arkid.core.translation import gettext_default as _
from arkid.core import routers, pages, actions

tag = 'tenant_statistics'
name = '租户数据分析'

page = pages.ChartPage(tag = tag, name = name)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/com_longgui_statistics_mysql/tenant_statistics/',
        method=actions.FrontActionMethod.GET,
    ),
)
