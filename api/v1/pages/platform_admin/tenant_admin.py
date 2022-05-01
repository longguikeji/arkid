# 所有租户列表/租户开关
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'tenant_admin'
name = '租户管理'

page = pages.TabsPage(name=name,tag=tag)
platform_config_page = pages.FormPage(name=_("平台配置"))
tenant_list_page = pages.TablePage(name=_("租户管理"))
edit_page = pages.FormPage(name=_("编辑租户"))


pages.register_front_pages(page)
pages.register_front_pages(tenant_list_page)
pages.register_front_pages(platform_config_page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.add_pages(
    [
        tenant_list_page,
        platform_config_page
    ]
)

platform_config_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/platform_config/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/platform_config/"
        ),
    }
)

tenant_list_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenants/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenants/',
        )
    },
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenants/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenants/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenants/{id}/"
        ),
    }
)


