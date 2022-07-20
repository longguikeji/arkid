from arkid.core.translation import gettext_default as _
from arkid.core import actions, pages, routers

tag = "mine_switch_tenant"
name = _("切换租户")

page = pages.CardsPage(
    tag=tag,
    name=name
)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='switch',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/mine/tenants/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenants/',
        )
    },
    local_actions={
        'switch_tenant': actions.URLAction(
            name=_('Switch', '切换'),
            path='/api/v1/mine/switch_tenant/{id}/',
            method=actions.FrontActionMethod.GET,
        ),
    },
)
