from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'third_auth'
name = '第三方认证'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑第三方认证"))
create_page = pages.FormPage(name=_("创建一个新的第三方认证"))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)
pages.register_front_pages(create_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/third_auths/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            page=create_page,
        )
    ],
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/third_auths/{id}/",
        )
    ],
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/third_auths/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/third_auths/{id}/"),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)

create_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/third_auths/',
        method=actions.FrontActionMethod.POST
    ),
    global_actions=[
        actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/third_auths/",
        ),
        actions.CancelAction(),
        actions.ResetAction(),
    ]
)
