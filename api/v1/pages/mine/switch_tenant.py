from arkid.core.translation import gettext_default as _
from arkid.core import actions, pages, routers
from django.conf import settings

tag = "mine_switch_tenant"
name = _("Switch Tenant", "切换租户")

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
            name=_("新建租户"),
            path='/api/v1/tenants/',
        )
    } if not settings.IS_CENTRAL_ARKID else {},
    local_actions={
        'switch_tenant': actions.DirectAction(
            name=_('Switch', '切换'),
            path='/api/v1/mine/switch_tenant/{id}/',
            method=actions.FrontActionMethod.GET,
        ),
    },
)
