from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'child_manager'
name = '子管理员'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑子管理员"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/child_managers/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/child_managers/',
        )
    ],
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/child_managers/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/child_managers/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/child_managers/{id}/"),

    ]
)


