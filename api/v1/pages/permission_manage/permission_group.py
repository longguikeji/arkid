from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'permission_group'
name = '权限分组'


page = pages.TreePage(tag=tag,name=name)
group_permissions_page = pages.TablePage(name=_("组内权限"))
edit_permissions_page = pages.TablePage(name=_("更新组内权限"))
create_page = pages.FormPage(name=_("创建权限分组"))
edit_page = pages.FormPage(name=_("编辑权限分组"))


pages.register_front_pages(page)
pages.register_front_pages(group_permissions_page)
pages.register_front_pages(edit_permissions_page)
pages.register_front_pages(create_page)
pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/',
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
            path="/api/v1/tenant/{tenant_id}/permission_groups/{id}/",
        )
    ],
    node_actions=[
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
    global_actions=[
        actions.OpenAction(
            name=_("添加权限"),
            page=edit_permissions_page,
        )
    ],
    local_actions=[
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/{id}/",
            icon="icon-delete",
        )
    ],
)


edit_permissions_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/{permission_group_id}/select_permissions/',
        method=actions.FrontActionMethod.GET,
    ),
    select=True,
    global_actions=[
        actions.ConfirmAction(
            path="/tenant/{tenant_id}/permission_groups/{permission_group_id}/permissions/"
        ),
        actions.CancelAction()
    ]
)


edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/permission_groups/{id}/"),

    ]
)

create_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/permission_groups/',
        method=actions.FrontActionMethod.POST
    ),
    global_actions=[
        actions.ConfirmAction(
            path="/api/v1/tenant/{tenant_id}/permission_groups/",
        ),

    ]
)
