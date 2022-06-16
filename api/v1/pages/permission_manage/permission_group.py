from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'permission_group'
name = '权限分组'


page = pages.TreePage(tag=tag,name=name)
group_permissions_page = pages.TablePage(name=_("组内权限"))
edit_permissions_page = pages.TablePage(name=_("更新组内权限"))

edit_page = pages.FormPage(name=_("编辑权限分组"))


pages.register_front_pages(page)
pages.register_front_pages(group_permissions_page)
pages.register_front_pages(edit_permissions_page)

pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
    icon='group',
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/all_apps_in_arkid/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions={
        'create': actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/permission_groups/',
        )
    },
    local_actions={
        "edit": actions.EditAction(
            page=edit_page,
        ),
        "delete":actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/permission_groups/{id}/",
        )
    },
    node_actions=[
        actions.DirectAction(
            path='/api/v1/tenant/{tenant_id}/permission_groups/?parent_id={id}',
            method=actions.FrontActionMethod.GET,
        ),
        actions.CascadeAction(
            page=group_permissions_page
        )
    ]
)

group_permissions_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
        "update":actions.OpenAction(
            name=_("添加权限"),
            page=edit_permissions_page,
        )
    },
    local_actions={
        "delete": actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/{id}/",
            icon="icon-delete",
        )
    },
)


edit_permissions_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/{permission_group_id}/select_permissions/',
        method=actions.FrontActionMethod.GET,
    ),
    select=True,
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/"
        ),
    }
)


edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions={
       'confirm': actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/permission_groups/{id}/"
        ),
    }
)


