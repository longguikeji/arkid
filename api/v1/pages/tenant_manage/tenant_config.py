from arkid.core import routers, pages, actions

tag = 'tenant_config'
name = '租户配置'

page = pages.FormPage(tag = tag, name = name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='settings',
)

page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenants/{tenant_id}/config/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions = {
        "confirm": actions.ConfirmAction(
            path="/api/v1/tenants/{tenant_id}/config/"
        ),
    }
)