from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'child_manager'
name = '子管理员'


page = pages.TablePage(tag=tag, name=name)
edit_page = pages.FormPage(name=_("编辑子管理员"))


pages.register_front_pages(page)
pages.register_front_pages(edit_page)

select_user_page = pages.TablePage(select=True,name=_("选择用户"))

pages.register_front_pages(select_user_page)

select_user_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/users/',
        method=actions.FrontActionMethod.GET
    )
)


select_permission_page = pages.TablePage(select=True,name=_("选择权限"))

pages.register_front_pages(select_permission_page)

select_permission_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/childmanager_permissions',
        method=actions.FrontActionMethod.GET
    )
)

select_scope_page = pages.TablePage(select=True,name=_("选择范围"))

pages.register_front_pages(select_scope_page)

select_scope_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/childmanager_permissions?only_show_group=1',
        method=actions.FrontActionMethod.GET
    )
)


router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='child',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/child_managers/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/child_managers/',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/child_managers/{id}/",
        )
    },
)

edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/child_managers/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/child_managers/{id}/",
            refresh=False
        ),
    }
)


