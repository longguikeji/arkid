from arkid.core import routers, pages, actions

tag = 'tenant_config'
name = '租户配置'

page = pages.FormPage(tag = tag, name = name)

pages.register_front_pages(page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page
)

page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/tenant_config/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions = [
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/tenant_config/"),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)