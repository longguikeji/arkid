# 所有租户列表/租户开关
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'tenant_admin'
name = '租户列表'

page = pages.TablePage(name=name,tag=tag)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)


page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenants/',
        method=actions.FrontActionMethod.GET,
    ),
    local_actions={
        "switch": actions.URLAction(
            name=_("切换"),
            path='/api/v1/mine/switch_tenant/{id}/',
            method=actions.FrontActionMethod.GET
        )
    },
)
