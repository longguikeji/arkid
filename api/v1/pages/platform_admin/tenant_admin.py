# 所有租户列表/租户开关
from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'tenant_admin'
name = '租户列表'

page = pages.TablePage(name=name,tag=tag)
edit_page = pages.FormPage(name=_("编辑租户"))

pages.register_front_pages(page)
pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='list',
)


page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenants/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenants/',
        )
    },
    local_actions={
        "switch": actions.URLAction(
            name=_("切换"),
            path='/api/v1/mine/switch_tenant/{id}/',
            method=actions.FrontActionMethod.GET
        ),
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenants/{id}/",
        )
    },
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