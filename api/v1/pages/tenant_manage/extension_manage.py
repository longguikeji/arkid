# 租户下的 extension的settings  config 
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'tenant_extension_manage'
name = '插件管理'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑插件"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extensions/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/extensions/',
        )
    ],
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/extensions/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/extensions/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/extensions/{id}/"),

    ]
)


