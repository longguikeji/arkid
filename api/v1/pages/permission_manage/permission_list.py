from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'permission_list'
name = '权限列表'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑权限"))


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
        path='/api/v1/tenant/{tenant_id}/permissions',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/permissions',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
            hidden='is_system'
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/permissions/{id}",
            hidden='is_system'
        ),
        # "toggle_open":actions.DirectAction(
        #     path="/api/v1/tenant/{tenant_id}/permission/{id}/toggle_open",
        #     method=actions.FrontActionMethod.POST,
        #     name=_("toggle open permission", "切换开放状态")
        # ),
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission/{permission_id}',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/permission/{permission_id}"
        ),
    }
)


