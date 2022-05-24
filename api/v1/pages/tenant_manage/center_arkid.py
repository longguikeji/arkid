# 中心平台

from arkid.core import routers, pages, actions

tag = 'center_arkid'
name = '中心平台'

page = pages.FormPage(tag = tag, name = name)
edit_page = pages.FormPage(name="编辑")
edit_slug_page = pages.FormPage(name="设置标识")

pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(edit_slug_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page
)

page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/bind_saas/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions = {
        "edit_slug": actions.EditAction(
            name="设置标识",
            page=edit_slug_page
        ),
        "confirm": actions.EditAction(
            page=edit_page
        ),
    }
)

edit_slug_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/bind_saas/slug/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions = {
        "confirm": actions.DirectAction(
            path="/api/v1/tenant/{tenant_id}/bind_saas/slug/",
            method=actions.FrontActionMethod.POST,
        ),
    }
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path="/api/v1/tenant/{tenant_id}/bind_saas/info/",
        method=actions.FrontActionMethod.GET,
    ),
    global_actions = {
        "confirm": actions.DirectAction(
            path="/api/v1/tenant/{tenant_id}/bind_saas/info/",
            method=actions.FrontActionMethod.POST,
        ),
    }
)