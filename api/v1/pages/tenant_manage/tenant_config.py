from arkid.core import routers, pages, actions

tag = 'tenant_config'
name = '租户配置'

page = pages.FormPage(tag = tag, name = name)
delete_tenant_page = pages.FormPage("注销租户")

pages.register_front_pages(page)
pages.register_front_pages(delete_tenant_page)

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
        "logout": actions.CreateAction(
            name="注销",
            path="/api/v1/tenants/{tenant_id}/logout/",
            method=actions.FrontActionMethod.POST,
        )
    }
)

delete_tenant_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenants/{tenant_id}/logout/",
        method=actions.FrontActionMethod.POST,
    ),
    global_actions={
        "confirm": actions.ConfirmAction(
            path="/api/v1/tenants/{tenant_id}/logout/"
        ),
    }
)