# 审批管理
from arkid.core.translation import gettext_default as _
from arkid.core import pages, routers, actions

tag = "mine_approve_request"
name = _("审批请求")


page = pages.TablePage(name=name, tag=tag)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/approve_requests/',
        method=actions.FrontActionMethod.GET,
    ),
)
