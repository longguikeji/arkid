# 授权管理
from select import select
from arkid.core.translation import gettext_default as _
from arkid.core import pages,routers,actions

tag = "mine_grant_manage"
name = _("授权管理")


page = pages.TablePage(
    name=name,
    tag=tag
)
permission_page = pages.TablePage(
    name=_("申请权限"),
    select=True,
)


pages.register_front_pages(page)
pages.register_front_pages(permission_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/permissions/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=actions.OpenAction(
        name=_("申请权限"),
        page=permission_page
    )
)

permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/all_permissions/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/mine/tenant/{tenant_id}/permissions/"),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)