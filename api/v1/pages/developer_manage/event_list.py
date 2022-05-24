# BI系统
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = "event_list"
name = _('Event List',"事件列表")

page = pages.TablePage(tag=tag,name=name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/event_list/',
        method=actions.FrontActionMethod.GET,
    ),
)