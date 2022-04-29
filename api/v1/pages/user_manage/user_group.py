from arkid.core import routers, pages, actions
from arkid.core.translation import gettext_default as _

tag = 'user_group'
name = '用户分组'


page = pages.TreePage(tag=tag,name=name)
group_users_page = pages.TablePage(name=_("组内用户"))
edit_users_page = pages.TablePage(name=_("更新组内用户"))

edit_page = pages.FormPage(name=_("编辑用户分组"))


pages.register_front_pages(page)
pages.register_front_pages(group_users_page)
pages.register_front_pages(edit_users_page)

pages.register_front_pages(edit_page)

router = routers.FrontRouter(
    path=tag,
    name=name,
    page=page,
)

page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/',
        method=actions.FrontActionMethod.GET,
    ),
    global_actions=[
        actions.CreateAction(
            path='/api/v1/tenant/{tenant_id}/user_groups/',
        )
    ],
    local_actions=[
        actions.EditAction(
            page=edit_page,
        ),
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/user_groups/{id}/",
        )
    ],
    node_actions=[
        actions.CascadeAction(
            page=group_users_page
        )
    ]
)

group_users_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/users/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.OpenAction(
            name=_("添加用户"),
            page=edit_users_page,
        )
    ],
    local_actions=[
        actions.DeleteAction(
            path="/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/users/{id}/",
            icon="icon-delete",
        )
    ],
)


edit_users_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/{user_group_id}/select_users/',
        method=actions.FrontActionMethod.GET,
    ),
    select=True,
    global_actions=[
        actions.ConfirmAction(
            path="/tenant/{tenant_id}/user_groups/{user_group_id}/users/"
        ),
    ]
)


edit_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/user_groups/{id}/',
        method=actions.FrontActionMethod.GET
    ),
    global_actions=[
        actions.ConfirmAction(path="/api/v1/tenant/{tenant_id}/user_groups/{id}/"),

    ]
)


