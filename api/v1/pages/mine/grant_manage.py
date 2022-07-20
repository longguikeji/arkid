# 授权管理
from select import select
from arkid.core.translation import gettext_default as _
from arkid.core import pages,routers,actions

tag = "mine_grant_manage"
name = _("授权管理")


page = pages.TreePage(
    name=name,
    tag=tag
)
app_permission_page = pages.TablePage(name=_("该应用权限"))
# permission_page = pages.TablePage(
#     name=_("申请权限"),
#     select=True,
# )


pages.register_front_pages(page)
pages.register_front_pages(app_permission_page)
# pages.register_front_pages(permission_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='app',
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/',
        method=actions.FrontActionMethod.GET,
    ),
    node_actions=[
        actions.CascadeAction(
            page=app_permission_page
        )
    ]
)

app_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenant/{tenant_id}/permissions/?app_id={app_id}',
        method=actions.FrontActionMethod.GET
    ),
)